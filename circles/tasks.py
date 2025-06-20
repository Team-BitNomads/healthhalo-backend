from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Sum
from .models import Circle, Membership, Contribution
from wallets.models import Wallet, Transaction
import logging

logger = logging.getLogger(__name__)

DELTAS = {
    'daily': timedelta(days=1),
    'weekly': timedelta(weeks=1),
    'monthly': timedelta(days=30)
}

def get_frequency_delta(frequency):
    return DELTAS.get(frequency, timedelta(weeks=1))

@shared_task
def enforce_contributions():
    for circle in Circle.objects.all():
        for membership in circle.membership_set.filter(is_active=True):
            user = membership.user
            wallet = Wallet.objects.filter(user=user).first()
            if not wallet:
                logger.warning(f"No wallet for user {user}")
                continue

            last_payment = membership.last_contribution_date or membership.join_date
            due_date = last_payment + get_frequency_delta(circle.frequency)

            if timezone.now() >= due_date:
                if wallet.balance >= circle.contribution_amount:
                    with transaction.atomic():
                        wallet.balance -= circle.contribution_amount
                        wallet.save()

                        circle.balance += circle.contribution_amount
                        circle.save()

                        Contribution.objects.create(
                            user=user,
                            circle=circle,
                            amount=circle.contribution_amount,
                            is_automatic=True
                        )

                        Transaction.objects.create(
                            wallet=wallet,
                            amount=circle.contribution_amount,
                            transaction_type='withdrawal',
                            description=f'Automatic contribution to {circle.name}'
                        )

                        membership.last_contribution_date = timezone.now()
                        membership.payment_warnings = 0
                        membership.save()
                else:
                    membership.payment_warnings += 1
                    membership.save()
                    logger.info(f"Warning increased for {user} in {circle.name}")

                    if membership.payment_warnings >= 2:
                        refund_and_remove_member(membership)

def refund_and_remove_member(membership):
    with transaction.atomic():
        total_contributed = Contribution.objects.filter(
            user=membership.user,
            circle=membership.circle,
            refunded=False
        ).aggregate(total=Sum('amount'))['total'] or 0

        if total_contributed > 0:
            if membership.circle.balance < total_contributed:
                logger.warning(f"Insufficient circle balance for refund to {membership.user}")
                return

            wallet = Wallet.objects.filter(user=membership.user).first()
            if not wallet:
                logger.warning(f"No wallet to refund user {membership.user}")
                return

            wallet.balance += total_contributed
            wallet.save()

            membership.circle.balance -= total_contributed
            membership.circle.save()

            Contribution.objects.filter(
                user=membership.user,
                circle=membership.circle,
                refunded=False
            ).update(refunded=True)

            Transaction.objects.create(
                wallet=wallet,
                amount=total_contributed,
                transaction_type='topup',
                description=f'Refund from {membership.circle.name}'
            )

        membership.is_active = False
        membership.save()

        logger.info(f"Deactivated and refunded user {membership.user} from {membership.circle.name}")
