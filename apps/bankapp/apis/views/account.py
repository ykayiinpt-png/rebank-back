from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.bankapp.apis.serializers.account import BankAccountSerializer
from apps.bankapp.apis.serializers.transaction import BankTransactionSerializer
from apps.bankapp.services.account import AccountService

class BankAccountListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankAccountSerializer
    
    def get(self, request):
        try:
            accounts = AccountService.list_accounts(request.user)
            serializer = BankAccountSerializer(accounts, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({ "message": str(e) }, status=status.HTTP_400_BAD_REQUEST)


class BankAccountCreateView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BankAccountSerializer
    
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
                return Response({ "message": str(e) }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class BankAccountDetailView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None
    
    def get(self, request, pk):
        try:
            account, historic_transactions = AccountService.detail_account(
                request.user, pk
            )
            
            return Response(
                {
                    "account": account, 
                    "transaction": BankTransactionSerializer(historic_transactions, many=True).data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({ "message": str(e) }, status=status.HTTP_400_BAD_REQUEST)
    

class BankAccountUpdateView(APIView):
    serializer_class = BankAccountSerializer
    
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
                return Response({ "message": str(e) }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)