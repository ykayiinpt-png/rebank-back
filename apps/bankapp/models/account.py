import os
import uuid
from django.db import models
from django.conf import settings

from apps.core.models.base import SoftDeletedModel, TimeStampedModel


def identity_upload_path(instance, filename):
    """Generate a UUID-based filename to prevent path traversal attacks."""
    ext = os.path.splitext(filename)[1].lower()
    return f'bank_account/identity/{uuid.uuid4().hex}{ext}'


class BankAccount(TimeStampedModel, SoftDeletedModel):
    first_name = models.CharField(null=False, blank=False, max_length=100)
    last_name = models.CharField(null=False, blank=False, max_length=100)

    identity_file = models.FileField(null=False, upload_to=identity_upload_path)
    
    approved = models.BooleanField(default=False, null=False)
    approved_at = models.DateTimeField(null=True)
    
    # After an approbation, a numero will be assigned
    numero = models.BigIntegerField(null=True)
    
    balance = models.BigIntegerField(default=0, null=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False
    )
    
    def __str__(self):
        return f"N° {self.numero} | {self.first_name} {self.last_name}"