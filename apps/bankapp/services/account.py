from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _t
from django.db.models import Q
from django.contrib.auth.models import AbstractUser

from apps.bankapp.models.account import BankAccount
from apps.bankapp.models.transaction import BankTransaction


class AccountService:
    
    @staticmethod
    def create_account(user: AbstractUser, first_name, last_name, identity_file):
        account = BankAccount.objects.create(
            first_name=first_name, last_name=last_name,
            identity_file=identity_file, user=user
        )
        
        return account
    
    @staticmethod
    def get_account(user: AbstractUser, account_pk: int):
        existing_acc = BankAccount.objects.filter(pk=account_pk, user=user).first()
        if existing_acc is None:
            raise ValidationError(_t("Le compte bancaire n'existe pas"))
        
        return existing_acc
    
    @staticmethod
    def update_account(user: AbstractUser, account_pk: int, first_name, last_name, identity_file):
        existing_acc = BankAccount.objects.filter(pk=account_pk, user=user).first()
        if existing_acc is None:
            raise ValidationError(_t("Le compte bancaire n'existe pas"))
        
        if existing_acc.approved:
             raise ValidationError(_t("Le compte bancaire a déjà été validé"))
        
        existing_acc.first_name=first_name
        existing_acc.last_name=last_name
        existing_acc.identity_file=identity_file
            
        existing_acc.save()
        
        return existing_acc
    
    
    @staticmethod
    def detail_account(user, account_pk):
        account = BankAccount.objects.filter(pk=account_pk, user=user).first()
        if account is None:
            raise ValidationError(_t("Le compte bancaire n'existe pas"))
        
        # List transactions
        historic_transactions = BankTransaction.objects.filter(
            Q(source_account=account) | Q(destination_account=account)
        ).order_by('-created_at').all()[:5]
        
        return account, historic_transactions
    
    @staticmethod
    def list_accounts(user: AbstractUser):
        accounts = BankAccount.objects.filter(user=user)
        return accounts
        
        