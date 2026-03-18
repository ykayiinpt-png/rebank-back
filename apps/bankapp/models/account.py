from django.db import models
from django.conf import settings

from apps.core.models.base import SoftDeletedModel, TimeStampedModel

class BankAccount(TimeStampedModel, SoftDeletedModel):
    first_name = models.CharField(null=False, blank=False)
    last_name = models.CharField(null=False, blank=False)
    
    identity_file = models.FileField(null=False, upload_to='bank_account/identity') # TODO add upload to
    
    approved = models.BooleanField(default=False, null=False)
    approved_at = models.DateTimeField(null=True)
    
    # After an approbation, a numero will be assigned
    numero = models.BigIntegerField(null=True)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=False
    )