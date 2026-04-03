from django.http import HttpRequest
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers as drf_serializers, status
from drf_spectacular.utils import extend_schema, inline_serializer

from apps.bankapp.apis.serializers.transaction import BankDepositSerializer, BankTransactionSerializer, BankTransferSerializer, BankWithdrawSerializer
from apps.bankapp.models.transaction import BankTransaction
from apps.bankapp.services.transaction import TransactionService

class BankTransactionListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(responses={200: BankTransactionSerializer(many=True)})
    def get(self, request: HttpRequest):
        try:
            transactions = TransactionService.list_transactions(request.user)
            serializer = BankTransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except Exception as e:
            message = str(e)
            if isinstance(e, ValidationError):
                message = e.message
            return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

class BankDepositAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankDepositSerializer

    @extend_schema(responses={200: {}})
    def post(self, request):
        serializer = BankDepositSerializer(data=request.data)

        if serializer.is_valid():
            try:
                transaction = TransactionService.deposit(
                    request.user,
                    serializer.validated_data['account_id'],
                    serializer.validated_data['amount']
                )

                return Response(
                    {},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BankWithdrawAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankWithdrawSerializer
    
    @extend_schema(responses={200: {}})
    def post(self, request):
        serializer = BankWithdrawSerializer(data=request.data)

        if serializer.is_valid():
            try:
                TransactionService.withdraw(
                    request.user,
                    serializer.validated_data['account_id'],
                    serializer.validated_data['amount']
                )

                return Response(
                    {},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BankTransferAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankTransferSerializer

    @extend_schema(responses={200: {}})
    def post(self, request):
        serializer = BankTransferSerializer(data=request.data)

        if serializer.is_valid():
            try:
                TransactionService.transfer(
                    request.user,
                    serializer.validated_data['source_account_id'],
                    serializer.validated_data['destination_account_numero'],
                    serializer.validated_data['amount']
                )

                return Response(
                    {},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecentContactsAPIView(APIView):
    """Return deduplicated recent transfer recipients for the current user."""
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: inline_serializer(
        name='RecentContact',
        fields={
            'numero': drf_serializers.IntegerField(),
            'first_name': drf_serializers.CharField(),
            'last_name': drf_serializers.CharField(),
        },
        many=True,
    )})
    def get(self, request):
        transfers = BankTransaction.objects.filter(
            source_account__user=request.user,
            transaction_type='TRANSFER',
            status='COMPLETED',
            destination_account__isnull=False,
        ).select_related('destination_account').order_by('-created_at')[:50]

        seen = set()
        contacts = []
        for tx in transfers:
            dest = tx.destination_account
            if dest.numero and dest.numero not in seen:
                seen.add(dest.numero)
                contacts.append({
                    'numero': dest.numero,
                    'first_name': dest.first_name,
                    'last_name': dest.last_name,
                })
            if len(contacts) >= 10:
                break

        return Response(contacts)