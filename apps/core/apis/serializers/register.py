from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _t


class RegisterSerializer(serializers.Serializer):
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


class RegisterResponseSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    otp_exp = serializers.FloatField()
    message = serializers.CharField()


class RegisterOtpSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)
    otp_exp = serializers.FloatField(required=True)
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _t("L'attribut email est requis")
        }
    )

