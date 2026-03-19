import datetime
import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _t
from django.utils import timezone
from django.conf import settings

from apps.core.services.user_account import generate_registration_token

logger = logging.getLogger(__name__)


UserModel = get_user_model()



class AuthService:
    
    @staticmethod
    def register_user(email: str, password: str):
        """
        Register a new user and sent email confirmation
        
        :returns user, is_success, verification_sent, verification_resent, check_email
        """
        
        user = None
        verification_sent = None
        verification_resent = None
        check_email = None
        
        # Validate user and email existence
        existing_user = UserModel.objects.filter(email=email).first()
        if existing_user is not None:
            # Check if user is active
            if existing_user.is_active:
                # We return an error message
                raise ValidationError(_t("Ce compte existe déjà; veuillez vérifier votre email"))
            else:
                # Check if we do have pass 1 hours since the first registration
                if timezone.now() - existing_user.updated_at > timedelta(hours=1) :
                    # We resend the account registration validation email
                    existing_user.save() # We do this in order to have updated_at updated
                        
                    generate_registration_token(email, True)
                    
                    verification_resent = True
                else:
                    # Call the user to check its email
                    check_email = True
        else:
            # Lutilisateur n'existe pas
            # on sauveagarde l'utilisateur et on lui envoi un mail
            user = UserModel.objects.create_user(email, password)
            generate_registration_token(email, True)
            verification_sent = True
            
        return user, verification_sent, verification_resent, check_email