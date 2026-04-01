from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _t


class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _t("L'attribut email est requis")
        }
    )


class ResetPasswordRequestResponseSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    otp_exp = serializers.FloatField()
    message = serializers.CharField()


class ResetPasswordOtpSerializer(serializers.Serializer):
    id_token = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)
    otp_exp = serializers.FloatField(required=True)
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _t("L'attribut email est requis")
        }
    )


class ResetPasswordOtpResponseSerializer(serializers.Serializer):
    reset_token = serializers.CharField()
    reset_exp = serializers.FloatField()


class ResetPasswordConfirmSerializer(serializers.Serializer):
    reset_token = serializers.CharField(required=True)
    reset_exp = serializers.FloatField(required=True)
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": _t("L'attribut email est requis")
        }
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        error_messages={
            "required": _t("L'attribut new_password est requis")
        }
    )
