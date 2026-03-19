from rest_framework import serializers

from apps.bankapp.models.transaction import BankTransaction

class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = '__all__'
        read_only_fields = ['id', 'status', 'reference', 'created_at']
        
class BankDepositSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)
    
class BankWithdrawSerializer(serializers.Serializer):
    account_id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)
    
class BankTransferSerializer(serializers.Serializer):
    source_account_id = serializers.IntegerField(required=True)
    destination_account_id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)