import logging
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _t
from django.contrib import messages
from django.views.decorators.http import require_GET, require_http_methods

from apps.bankapp.forms.account import BankAccountForm
from apps.bankapp.models.account import BankAccount
from apps.bankapp.services.account import AccountService
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
            try:
                AccountService.create_account(
                    request.user,
                    form.cleaned_data['first_name'],
                    form.cleaned_data['last_name'],
                    form.cleaned_data['identity_file']
                )
                
                messages.success(request, _t("Compte bancaire créé avec succès"))
                
                return redirect('bankapp-account-list')
            except Exception as e:
                messages.error(request, str(e), extra_tags="danger")    
    else:
        form = BankAccountForm()
    
    return render(
        request,
        'client/account/create.html',
        {
            'form': form
        }
    )

@require_http_methods(["GET", "POST"])
@app_login_required()
def update_account(request: HttpRequest, pk: int):
    """
    Update non approved account
    """
    form = None
    existing_acc = None
    
    if request.method == "POST":
        form = BankAccountForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                AccountService.update_account(
                    request.user, pk,
                    form.cleaned_data['first_name'], form.cleaned_data['last_name'],
                    form.cleaned_data['identity_file']
                )
                    
                messages.success(request, _t("Compte bancaire mise à jour avec succès"))
                    
                return redirect('bankapp-account-list')
            except Exception as e:
                messages.error(request, str(e), extra_tags="danger")    

    else:
        try:
            existing_acc = AccountService.get_account(
                request.user, pk,
            )
        except Exception as e:
            messages.error(request, str(e), extra_tags="danger")   
            return redirect('bankapp-account-list')
                
        form = BankAccountForm(
            data={
                "first_name": existing_acc.first_name,
                "last_name": existing_acc.last_name,
                "last_identity_file": existing_acc.identity_file}
        )
    
    return render(
        request,
        'client/account/update.html',
        {
            'form': form,
            "account": existing_acc
        }
    )
    
@require_GET
@app_login_required()
def detail_account(request: HttpRequest, pk: int):
    """
    Update non approved account
    """
    
    try:
        account, historic_transactions = AccountService.detail_account(
            request.user,
            pk
        )
    except Exception as e:
        messages.error(request, str(e), extra_tags="danger")
        return redirect('bankapp-account-list')
    
    return render(
        request,
        'client/account/detail.html',
        {
            "account": account,
            'historic_transactions': historic_transactions
        }
    )
    
    
@require_GET
@app_login_required()
def list_accounts(request: HttpRequest):
    """
    List the current authenticated user
    """
    try:
        accounts = AccountService.list_accounts(request.user)
    except Exception as e:
        messages.error(request, str(e), extra_tags="danger")
        return redirect('client-account-dashboard')
    
    return render(
        request,
        'client/account/list.html',
        {
            'accounts': accounts
        }
    )
    