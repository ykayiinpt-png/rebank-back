from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _t

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _t("L'attribut email est requis")
        }
    )

    password = serializers.CharField(
        required=True,
        validators=[validate_password],
        error_messages={
            "required": _t("L'attribut password est requis")
        }
    )
    
class LoginResponseSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    otp_exp = serializers.FloatField()
    
class LoginOtpSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)
    otp_exp = serializers.FloatField(required=True)
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _t("L'attribut email est requis")
        }
    )
    
class LoginTokensSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()