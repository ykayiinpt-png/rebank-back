from rest_framework import serializers

from apps.bankapp.models.account import BankAccount
from apps.bankapp.models.transaction import BankTransaction

class BankTransactionAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = ["numero", "first_name", "last_name"]

class BankTransactionSerializer(serializers.ModelSerializer):
    source_account = BankTransactionAccountSerializer(read_only=True)
    destination_account = BankTransactionAccountSerializer(read_only=True)
    
    class Meta:
        model = BankTransaction
        #fields = '__all__'
        exclude = ['user']
        read_only_fields = ['id', 'status', 'reference', 'created_at']
        
class BankDepositSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)
    
class BankWithdrawSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)
    
class BankTransferSerializer(serializers.Serializer):
    source_account_id = serializers.IntegerField(required=True)
    destination_account_numero = serializers.CharField(required=True)
    amount = serializers.IntegerField(required=True)