from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.bankapp.apis.serializers.transaction import BankDepositSerializer, BankTransactionSerializer, BankTransferSerializer, BankWithdrawSerializer
from apps.bankapp.models.transaction import BankTransaction
from apps.bankapp.services.transaction import TransactionService

class BankTransactionListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankTransactionSerializer

    def get(self, request: HttpRequest):
        transactions = BankTransaction.objects.filter(user=request.user)
        serializer = BankTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class BankDepositAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankDepositSerializer

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
                    BankTransactionSerializer(transaction).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BankWithdrawAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankWithdrawSerializer

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
                return Response({"message": str(e)}, status=status.HTTP_417_EXPECTATION_FAILED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BankTransferAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankTransferSerializer

    def post(self, request):
        serializer = BankTransferSerializer(data=request.data)

        if serializer.is_valid():
            try:
                TransactionService.transfer(
                    request.user,
                    serializer.validated_data['source_account_id'],
                    serializer.validated_data['destination_account_id'],
                    serializer.validated_data['amount']
                )

                return Response(
                    {},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_417_EXPECTATION_FAILED)
            

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)