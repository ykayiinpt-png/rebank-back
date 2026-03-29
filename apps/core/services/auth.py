import datetime
import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _t
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate

from apps.core.helpers.time import timestamp_has_expired
from apps.core.models.auth import BaseUserSession
from apps.core.services.user_account import (
    generate_registration_token, send_login_otp, validate_login_otp_signature,
    send_registration_otp, validate_registration_otp_signature
)

logger = logging.getLogger(__name__)


UserModel = get_user_model()



class AuthService:
    
    @staticmethod
    def register_user(email: str, password: str, use_otp: bool = False):
        """
        Register a new user and send verification email.

        When use_otp=True (mobile app): sends an OTP code by email.
        :returns user, id_token, otp_exp, verification_sent, verification_resent, check_email

        When use_otp=False (web, default): sends a token link by email (original behavior).
        :returns user, verification_sent, verification_resent, check_email
        """

        user = None
        id_token = None
        otp_exp = None
        verification_sent = None
        verification_resent = None
        check_email = None

        # Validate user and email existence
        existing_user = UserModel.objects.filter(email=email).first()
        if existing_user is not None:
            # Check if user is active
            if existing_user.is_active:
                raise ValidationError(_t("Ce compte existe déjà; veuillez vérifier votre email"))
            else:
                # Check if we do have pass 1 hours since the first registration
                if timezone.now() - existing_user.updated_at > timedelta(hours=1) :
                    existing_user.save()
                    if use_otp:
                        id_token, otp_exp = send_registration_otp(email, True)
                    else:
                        generate_registration_token(email, True)
                    verification_resent = True
                else:
                    check_email = True
        else:
            user = UserModel.objects.create_user(email, password)
            if use_otp:
                id_token, otp_exp = send_registration_otp(email, True)
            else:
                generate_registration_token(email, True)
            verification_sent = True

        if use_otp:
            return user, id_token, otp_exp, verification_sent, verification_resent, check_email
        else:
            return user, verification_sent, verification_resent, check_email

    @staticmethod
    def register_verify_otp(id_token: str, otp: str, exp: float, email: str):
        """
        Validate the registration OTP and activate the user account.

        :returns user
        """

        if validate_registration_otp_signature(email, otp, id_token):
            if not timestamp_has_expired(exp):
                user = UserModel.objects.filter(email=email).first()
                if user is not None:
                    user.is_active = True
                    user.save()
                    return user
                else:
                    raise ValidationError(_t("Utilisateur introuvable"))
            else:
                raise ValidationError(_t("Le code OTP a expiré"))
        else:
            raise ValidationError(_t("Le code OTP est invalide"))
    
    @staticmethod
    def login_user(email: str, password: str):
        """
        Check user existance and password then send otp
        for 2FA
        
        :returns 
        id_token, otp_exp
        """
        
        user = None
        
        # Authenticate user
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise ValidationError(_t("Vos identifiants sont incorrects"))
    
        if user.check_password(password + user.salt):
            raise ValidationError(_t("Vos identifiants sont incorrects"))
        
        
        # We make sure that we do not have a valid user session
        existing_login_session = BaseUserSession.objects.filter(
            email=user.email, is_valid=True
        ).order_by('-created_at').first()
        
        # A valid and non expired login session
        if (existing_login_session is not None) and \
            (not timestamp_has_expired(expiry_datetime=existing_login_session.exp)):
            # A session exists and has not logged out yet
            raise ValidationError(_t("Une session d'utilisateur existe déjà. Veuillez vous déconnecter"))
        
        # Generate otp and send by email
        id_token, otp_exp = send_login_otp(email, True)
        
        return id_token, otp_exp
        
    @staticmethod
    def login_user_otp(id_token: str, otp: str, exp: float, email: str):
        """
        Validate user token and login user.
        
        :returns
        user
        """
        
        if validate_login_otp_signature(email, otp, id_token):
            if not timestamp_has_expired(exp):
                # They are equal we log in the user
                user = UserModel.objects.filter(email=email).first()
                if user is not None:
                    # Save a new login session for the authenticated user
                    BaseUserSession.objects.create(
                        email=email,
                        exp=timezone.now() + timedelta(minutes=settings.LOGIN_SESSION_EXPIRE_MINUTES)
                    )
                    
                    return user
                else:
                    logger.error("User received OTP but does not exists")
                    raise ValidationError(_t("Une erreur s'est produite, veuillez réessayer")) 
            else:
               raise ValidationError(_t("Votre session est expiré")) 
        else:
            raise ValidationError(_t("Vos informations sont invalide"))
        