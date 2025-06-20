from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class WalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get wallet details and transaction history
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response(
                {"error": "Wallet not found. Please make your first top-up to create a wallet."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WalletSerializer(wallet)
        transactions = wallet.transactions.all().order_by('-timestamp')
        transaction_serializer = TransactionSerializer(transactions, many=True)
        
        response_data = {
            'wallet': serializer.data,
        }
        return Response(response_data)

    def post(self, request):
        # Handle top-up or withdrawal
        amount = request.data.get('amount')
        transaction_type = request.data.get('transaction_type')  # 'topup' or 'withdrawal'

        if not amount or not transaction_type:
            return Response(
                {"error": "Amount and transaction_type are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Amount must be a positive number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if transaction_type not in ['topup', 'withdrawal']:
            return Response(
                {"error": "Invalid transaction type. Must be 'topup' or 'withdrawal'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create wallet
        wallet, created = Wallet.objects.get_or_create(user=request.user)

        if transaction_type == 'withdrawal':
            if wallet.balance < amount:
                return Response(
                    {"error": "Insufficient balance. Please top up your wallet."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            wallet.balance -= int(amount)
        else:  # topup
            wallet.balance += int(amount)

        wallet.save()

        # Create transaction record
        transaction = Transaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=transaction_type,
            description=request.data.get('description', '')
        )

        serializer = WalletSerializer(wallet)
        return Response(serializer.data, status=status.HTTP_200_OK)