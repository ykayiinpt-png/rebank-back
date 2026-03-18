import logging
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _t
from django.contrib import messages
from django.views.decorators.http import require_GET, require_http_methods

from apps.bankapp.forms import BankAccountForm
from apps.bankapp.models.account import BankAccount
from apps.core.decorators.auth import app_login_required

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
@app_login_required()
def create_account(request: HttpRequest):
    """
    Create a bank account 
    """
    form = None
    
    if request.method == "POST":
        form = BankAccountForm(request.POST, request.FILES)
        
        if form.is_valid():
            print("Form is valid")
            
            BankAccount.objects.create(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                identity_file=form.cleaned_data['identity_file'],
                user=request.user
            )
            
            messages.success(request, _t("Compte bancaire créé avec succès"))
            
            return redirect('bankapp-account-list')
        
        print("Form is not valid")
    else:
        form = BankAccountForm()
    
    return render(
        request,
        'client/account/create.html',
        {
            'form': form
        }
    )
    
@require_GET
@app_login_required()
def list_accounts(request: HttpRequest):
    """
    List the current authenticated user
    """
    
    accounts = BankAccount.objects.filter(user=request.user)
    
    return render(
        request,
        'client/account/list.html',
        {
            'accounts': accounts
        }
    )
    