from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _t
from django.db.models import Q

from apps.bankapp.models.account import BankAccount
from apps.bankapp.models.transaction import BankTransaction


class TransactionService:
    
    @staticmethod
    def list_transactions(user: AbstractUser):
        transactions = BankTransaction.objects.filter(
            Q(source_account__user=user) | Q(destination_account__user=user)
        ).order_by('-created_at').all()
        
        return transactions

    @staticmethod
    @transaction.atomic
    def deposit(user: AbstractUser, account_pk: int, amount: int):
        if amount <= 0:
            raise ValidationError(_t("Le montant doit être positif."))
        
        # Lock the row
        account = BankAccount.objects.select_for_update().filter(pk=account_pk, user=user).first()
        if account is None:
            raise ValidationError(_t("Le compte bancaire n'existe pas"))
        
        if not account.approved:
            raise ValidationError(_t("Le compte bancaire non actif"))

        account.balance += amount
        account.save()

        return BankTransaction.objects.create(
            user=user,
            transaction_type='DEPOSIT',
            amount=amount,
            destination_account=account,
            status='COMPLETED',
            balance_after=account.balance
        ), None

    @staticmethod
    @transaction.atomic
    def withdraw(user: AbstractUser, account_pk: int, amount: int):
        if amount <= 0:
            raise ValidationError("Montant invalide.")
        
        # Lock the row
        account = BankAccount.objects.select_for_update().filter(pk=account_pk, user=user).first()
        if account is None:
            raise ValidationError(_t("Le compte bancaire n'existe pas"))
        
        if not account.approved:
            raise ValidationError(_t("Le compte bancaire non actif"))
        
        if account.balance < amount:
            raise ValidationError(_t("Solde insuffisant."))

        account.balance -= amount
        account.save()

        return BankTransaction.objects.create(
            user=user,
            transaction_type='WITHDRAWAL',
            amount=amount,
            source_account=account,
            status='COMPLETED',
            balance_after=account.balance
        ), None

    @staticmethod
    @transaction.atomic
    def transfer(user: AbstractUser, source_account_pk: int, destination_account_n: int, amount: int):        
        # Lock the row
        source_account = BankAccount.objects.select_for_update().filter(pk=source_account_pk, user=user).first()
        if source_account is None:
            raise ValidationError(_t("Le compte bancaire source n'existe pas"))
        
        if str(source_account.numero) == destination_account_n:
            raise ValidationError(_t("Impossible de transférer vers le même compte."))
        
        if not source_account.approved:
            raise ValidationError(_t("Le compte bancaire source non actif"))
        
        destination_account = BankAccount.objects.select_for_update().filter(numero=destination_account_n).first()
        if destination_account is None:
            raise ValidationError(_t("Le compte bancaire destinataire n'existe pas"))
        
        if not destination_account.approved:
            raise ValidationError(_t("Le compte bancaire destinataire non actif"))
        
        if source_account.balance < amount:
            raise ValidationError(_t("Solde insuffisant."))

        source_account.balance -= amount
        destination_account.balance += amount

        source_account.save()
        destination_account.save()

        return BankTransaction.objects.create(
            user=user,
            transaction_type='TRANSFER',
            amount=amount,
            source_account=source_account,
            destination_account=destination_account,
            status='COMPLETED',
            balance_after=source_account.balance
        )