import random
import string

from django.conf import settings

def otp_generate():
    """
    Generates a random 6-digit string for OTP
    """
    return ''.join(random.choice(string.digits) for _ in range(settings.OTP_LENGTH))