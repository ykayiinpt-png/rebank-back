# accounts/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator,
    CommonPasswordValidator,
    NumericPasswordValidator
)


class CustomUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):

    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Votre mot de passe ressemble trop à vos informations personnelles.")
            )

    def get_help_text(self):
        return _("Votre mot de passe ne doit pas ressembler à vos informations personnelles.")


class CustomMinimumLengthValidator(MinimumLengthValidator):

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Le mot de passe doit comporter au moins %(min_length)d caractères."),
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return _("Le mot de passe doit comporter au moins %(min_length)d caractères.") % {
            "min_length": self.min_length
        }


class CustomCommonPasswordValidator(CommonPasswordValidator):

    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Ce mot de passe est trop courant. Veuillez en choisir un plus sûr.")
            )

    def get_help_text(self):
        return _("Votre mot de passe ne doit pas être un mot de passe couramment utilisé.")


class CustomNumericPasswordValidator(NumericPasswordValidator):

    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Le mot de passe ne peut pas être composé uniquement de chiffres.")
            )

    def get_help_text(self):
        return _("Votre mot de passe ne peut pas être composé uniquement de chiffres.")