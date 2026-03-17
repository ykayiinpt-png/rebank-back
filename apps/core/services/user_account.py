import logging
from django.conf import settings

from apps.core.helpers.hash import hmac_sha256_hash
from apps.core.helpers.mail import send_template_email


logger = logging.getLogger(__name__)

def generate_registration_token(email, send=False):
    """
    After a registration a token is generated base on the
    email of the user using the key signed based hashing HMAC
    """
    
    token = hmac_sha256_hash(settings.HMAC_SECRET, email)
    url = settings.URL_REGISTATION_VALIDATION.format(token, email)
    logging.info(f"Url generated: {url}")
    send_template_email(
        "Validation Création de Compte",
        "client_registration_to_validate",
        { "url": url },
        email
    )
    
    return token

def validate_registration_token(email, input_token):
    """
    Validate the provided token against the one generated
    """
    return input_token == hmac_sha256_hash(settings.HMAC_SECRET, email)
    
    
    