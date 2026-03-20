from django import forms
from django.utils.translation import gettext as _t
from django.db.models import Q

from apps.bankapp.models.account import BankAccount

class BankDepositForm(forms.Form):
    account = forms.ChoiceField(
        choices=[],
        required=True,
        label=_t("Compte Bancaire")
    )
    amount = forms.IntegerField(
        required=True,
        min_value=1,
        label=_t("Montant")
    )

    def __init__(self, *args, user=None, accounts=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['account'].choices = [ (m.pk, str(m)) for m in  BankAccount.objects.filter(user=user, approved=True)]
            
        if accounts:
            self.fields['account'].choices = [ (m.pk, str(m)) for m in accounts ]
            
            
class BankWithdrawForm(forms.Form):
    account = forms.ChoiceField(
        choices=[],
        label=_t("Compte Bancaire")
    )
    amount = forms.IntegerField(
        min_value=1,
        label=_t("Montant")
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
             self.fields['account'].choices = [ (m.pk, str(m)) for m in  BankAccount.objects.filter(user=user, approved=True)]

    
class BankTransferForm(forms.Form):
    source_account = forms.ChoiceField(
        choices=[],
        label=_t("Compte Bancaire Source")
    )
    destination_account = forms.CharField(
        label=_t("Compte Bancaire destinataire")
    )
    amount = forms.IntegerField(
        min_value=1,
        label=_t("Montant")
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['source_account'].choices = [ (m.pk, str(m)) for m in  BankAccount.objects.filter(user=user, approved=True)]

    def clean(self):
        cleaned_data = super().clean()
        
        cleaned_data['destination_account'] = int(cleaned_data.get('destination_account'))

        return cleaned_data