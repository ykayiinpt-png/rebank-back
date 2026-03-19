from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, inline_serializer

from apps.bankapp.apis.serializers.account import BankAccountResponseSerializer, BankAccountSerializer
from apps.bankapp.apis.serializers.transaction import BankTransactionSerializer
from apps.bankapp.services.account import AccountService

class BankAccountListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(responses={200: BankAccountResponseSerializer(many=True)})
    def get(self, request):
        try:
            accounts = AccountService.list_accounts(request.user)
            serializer = BankAccountResponseSerializer(accounts, many=True)
            return Response(serializer.data)
        except Exception as e:
            message = str(e)
            if isinstance(e, ValidationError):
                message = e.message
            return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)


class BankAccountCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankAccountSerializer
    
    @extend_schema(responses={200: {}})
    def post(self, request):
        serializer = BankAccountSerializer(data=request.data)
        if serializer.is_valid():
            try:
                AccountService.create_account(
                    request.user,
                    serializer.validated_data['first_name'], serializer.validated_data['last_name'],
                    serializer.validated_data['identity_file']
                    
                )
                return Response({
                    "message": "Compte créé avec succès",
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BankAccountDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: inline_serializer(
            name="AccountWithTransactions",
            fields={
                "account": BankAccountResponseSerializer(),
                "transaction": BankTransactionSerializer(many=True),
            }
        )
    })
    def get(self, request, pk):
        try:
            account, historic_transactions = AccountService.detail_account(
                request.user, pk
            )
            
            return Response(
                {
                    "account": BankAccountResponseSerializer(account).data, 
                    "transaction": BankTransactionSerializer(historic_transactions, many=True).data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            message = str(e)
            if isinstance(e, ValidationError):
                message = e.message
            return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)
    

class BankAccountUpdateView(APIView):
    serializer_class = BankAccountSerializer
    
    @extend_schema(responses={200: {}})
    def put(self, request, pk):
        serializer = BankAccountSerializer(data=request.data)

        if serializer.is_valid():
            try:
                AccountService.update_account(
                    request.user,
                    pk,
                    serializer.validated_data['first_name'], serializer.validated_data['last_name'],
                    serializer.validated_data['identity_file']
                    
                )
                return Response({
                    "message": "Compte Mis à jour avec succès",
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)