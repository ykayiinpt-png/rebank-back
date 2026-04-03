import os
from rest_framework import serializers

from apps.bankapp.models.account import BankAccount

# 5 MB max file size
MAX_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}
# Magic bytes for file type verification
MAGIC_BYTES = {
    b'\xff\xd8\xff': 'image/jpeg',
    b'\x89PNG': 'image/png',
    b'%PDF': 'application/pdf',
}

class BankAccountSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True, max_length=100)
    last_name = serializers.CharField(required=True, max_length=100)
    identity_file = serializers.ImageField(required=True)

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le prénom ne peut pas être vide")
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Le nom ne peut pas être vide")
        return value.strip()

    def validate_identity_file(self, value):
        # Check file size
        if value.size > MAX_UPLOAD_SIZE:
            raise serializers.ValidationError("Le fichier ne doit pas dépasser 5 Mo")

        # Check extension
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Extension non autorisée. Formats acceptés : {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Verify magic bytes (file content matches claimed type)
        header = value.read(8)
        value.seek(0)  # Reset file pointer
        valid_type = False
        for magic, _ in MAGIC_BYTES.items():
            if header.startswith(magic):
                valid_type = True
                break
        if not valid_type:
            raise serializers.ValidationError(
                "Le contenu du fichier ne correspond pas à un format d'image ou PDF valide"
            )

        return value
    
class BankAccountResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'