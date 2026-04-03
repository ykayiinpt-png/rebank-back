import secrets
import string

from django.conf import settings

def otp_generate():
    """
    Generates a cryptographically secure random OTP
    """
    return ''.join(secrets.choice(string.digits) for _ in range(settings.OTP_LENGTH))