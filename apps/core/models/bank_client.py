from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models.base_user import BaseUser

class BankClient(models.Model):
    """
    Custom user model that extends the default Django user.
    Keeps username-based auth but adds extra fields.
    """
    
    user = models.OneToOneField(BaseUser, on_delete=models.PROTECT)
    
    class Meta:
        # Useful for admin and debugging
        verbose_name = 'Bank Client User'
        verbose_name_plural = 'Bank Client Users'