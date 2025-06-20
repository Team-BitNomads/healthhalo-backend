from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import Circle, Contribution, Claim, Membership
from .serializers import CircleSerializer, ContributionSerializer, ClaimSerializer, MembershipSerializer
from wallets.models import Wallet, Transaction
from .utils import validate_claim

class CircleListCreateView(generics.ListCreateAPIView):
    serializer_class = CircleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Circle.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        circle = serializer.save(creator=self.request.user)
        Membership.objects.create(user=self.request.user, circle=circle)


class CircleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CircleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Circle.objects.filter(members=self.request.user)


class ContributionView(generics.CreateAPIView):
    serializer_class = ContributionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        circle = get_object_or_404(Circle, id=self.kwargs['circle_id'])
        membership = get_object_or_404(Membership, user=self.request.user, circle=circle, is_active=True)

        try:
            wallet = Wallet.objects.get(user=self.request.user)
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet not found for user.")

        if wallet.balance < circle.contribution_amount:
            raise serializers.ValidationError("Insufficient wallet balance")

        with transaction.atomic():
            wallet.balance -= circle.contribution_amount
            wallet.save()

            circle.balance += circle.contribution_amount
            circle.save()

            Transaction.objects.create(
                wallet=wallet,
                amount=circle.contribution_amount,
                transaction_type='withdrawal',
                description=f'Contribution to {circle.name} circle'
            )

            serializer.save(
                user=self.request.user,
                circle=circle,
                amount=circle.contribution_amount
            )

            membership.last_contribution_date = timezone.now()
            membership.payment_warnings = 0
            membership.save()


class ClaimCreateView(generics.CreateAPIView):
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        circle = get_object_or_404(Circle, id=self.kwargs['circle_id'])
        membership = get_object_or_404(Membership, user=self.request.user, circle=circle, is_active=True)

        if (timezone.now() - membership.join_date).days < circle.claim_lock_period:
            raise serializers.ValidationError(
                f"You cannot file claims within {circle.claim_lock_period} days of joining"
            )

        claim = serializer.save(user=self.request.user, circle=circle, status='pending')
        try:
            claim.full_clean()
        except serializers.ValidationError as e:
            claim.delete()  # Remove invalid claim
            raise serializers.ValidationError(e.detail if hasattr(e, 'detail') else str(e))

        # AI validation
        is_valid, reason = validate_claim(claim)

        if is_valid:
            if claim.circle.balance < claim.amount:
                claim.status = 'rejected'
                claim.processed_at = timezone.now()
                claim.save()
                raise serializers.ValidationError("Insufficient circle balance")

            with transaction.atomic():
                user_wallet = Wallet.objects.get(user=claim.user)
                user_wallet.balance += claim.amount
                user_wallet.save()

                claim.circle.balance -= claim.amount
                claim.circle.save()

                Transaction.objects.create(
                    wallet=user_wallet,
                    amount=claim.amount,
                    transaction_type='topup',
                    description=f'Payout from {claim.circle.name} for claim'
                )

                claim.status = 'approved'
                claim.processed_at = timezone.now()
                claim.save()
        else:
            claim.status = 'rejected'
            claim.processed_at = timezone.now()
            claim.save()
            raise serializers.ValidationError(f"Claim rejected: {reason}")


class MembershipListView(generics.ListAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        circle = get_object_or_404(Circle, id=self.kwargs['circle_id'])
        return Membership.objects.filter(circle=circle)
