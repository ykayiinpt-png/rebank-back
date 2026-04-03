from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from apps.core.managers.user_manager import AppBaseUserManager
from .base import TimeStampedModel, SoftDeletedModel

class BaseUser(AbstractUser, PermissionsMixin, TimeStampedModel, SoftDeletedModel):
    """
    A base user of the ebank application. It may be a client or a bank
    personnel
    """
    email = models.EmailField(
        unique=True,
        error_messages={
            'unique': 'Un utilisateur avec cet email existe déjà.'
        }
    )
    
    salt = models.CharField(null=False, max_length=50)
    
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # 2FA — user must opt-in before OTP is enforced on login
    two_factor_enabled = models.BooleanField(default=False)

    # Track when the profile was last updated
    profile_updated_at = models.DateTimeField(auto_now=True)

    # For soft-delete functionality
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    
    objects = AppBaseUserManager()
    
    # Meta definition
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        # Useful for admin and debugging
        verbose_name = 'EBank User'
        verbose_name_plural = 'EBank Users'

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    