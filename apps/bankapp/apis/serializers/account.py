from rest_framework import serializers

from apps.bankapp.models.account import BankAccount

class BankAccountSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    identity_file = serializers.ImageField(required=True)

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le prénom ne peut pas être vide")
        return value

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le nom ne peut pas être vide")
        return value
    
class BankAccountResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'