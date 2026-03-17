import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from apps.core.helpers.hash import hmac_sha256_hash
from apps.core.helpers.mail import send_template_email
from apps.core.helpers.otp import otp_generate


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

def send_login_otp(email, send=True):
    """
    Generates an OTP, sends it to the provided email and retuns the identifier token
    and it expiry date in timestamp
    """
    
    otp = otp_generate()
    expiry_time = timezone.now() + timedelta(minutes=settings.OTP_EXP_DURATION_MINUTES)
    
    input = f"{email}-{otp}"
    token = hmac_sha256_hash(settings.HMAC_SECRET, input)
    
    if send:
        send_template_email(
            "Conexion - OTP",
            "client_login_otp",
            { "otp": otp },
            email
        )
        
    return token, expiry_time.timestamp()

def validate_login_otp_signature(email: str, otp: str, id_token: str):
    """
    Validate a provided OTP agains a generated one
    """
    input = f"{email}-{otp}"
    expect_token = hmac_sha256_hash(settings.HMAC_SECRET, input)
    
    return expect_token == id_token
    
    