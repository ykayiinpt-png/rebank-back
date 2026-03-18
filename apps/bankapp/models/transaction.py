import uuid

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from apps.bankapp.models.account import BankAccount
from apps.core.models.base import SoftDeletedModel, TimeStampedModel

class BankTransaction(TimeStampedModel, SoftDeletedModel):
    
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Dépôt'),
        ('WITHDRAWAL', 'Retrait'),
        ('TRANSFER', 'Virement'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('COMPLETED', 'Complétée'),
        ('FAILED', 'Échouée'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT )
    source_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='outgoing_transactions',
        null=True,
        blank=True
    )
    destination_account = models.ForeignKey(
        BankAccount,
        on_delete=models.CASCADE,
        related_name='incoming_transactions',
        null=True,
        blank=True
    )

    # Transaction detail
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField(null=False)
    balance_after = models.IntegerField(null=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Metadata
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} ({self.status})"
    
    
    def clean(self):
        if self.transaction_type == 'TRANSFER':
            if not self.source_account or not self.destination_account:
                raise ValidationError("Un virement nécessite deux comptes.")

        if self.transaction_type == 'WITHDRAWAL' and not self.source_account:
            raise ValidationError("Un retrait nécessite un compte source.")
        
    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = str(uuid.uuid4()).replace('-', '').upper()[:12]
            
        super().save(*args, **kwargs)
        
        