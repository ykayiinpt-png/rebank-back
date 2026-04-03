from django.db.models import Q
from django.http import HttpRequest
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from apps.bankapp.forms.transaction import BankDepositForm, BankTransferForm, BankWithdrawForm
from apps.bankapp.models.transaction import BankTransaction
from apps.bankapp.services.transaction import TransactionService
from apps.core.decorators.auth import app_login_required



@require_GET
@app_login_required()
def detail_transaction(request: HttpRequest, pk: int):
    transaction = BankTransaction.objects.filter(
        pk=pk
    ).filter(
        Q(source_account__user=request.user) |
        Q(destination_account__user=request.user) |
        Q(user=request.user)
    ).first()

    if transaction is None:
        messages.error(request, "Transaction introuvable", extra_tags="danger")
        return redirect('bankapp-account-list-transactions')

    return render(
        request,
        'client/account/transactions/detail.html',
        {'transaction': transaction}
    )


@require_GET
@app_login_required()
def list_transactions(request: HttpRequest):
    try:
        transactions = TransactionService.list_transactions(request.user)
    except Exception as e:
        messages.error(request, str(e), extra_tags="danger")
        return redirect('bankapp-account-list')
    
    return render(
        request,
        "client/account/transactions/list.html",
        {
            'transactions': transactions
        }
    )

@require_http_methods(["GET", "POST"])
@app_login_required()
def deposit(request: HttpRequest):
    form = BankDepositForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        account = form.cleaned_data['account']
        amount = form.cleaned_data['amount']

        try:
            TransactionService.deposit(request.user, account, amount)
            messages.success(request, "Dépôt réussi.")
            return redirect('bankapp-account-list')
        except Exception as e:
            messages.error(request, str(e), extra_tags="danger")

    return render(
        request,
        'client/account/deposit.html',
        {
            'form': form
        }
    )

@app_login_required()
def withdraw(request):
    form = BankWithdrawForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        account = form.cleaned_data['account']
        amount = form.cleaned_data['amount']

        try:
            TransactionService.withdraw(request.user, account, amount)
            messages.success(request, "Retrait réussi.")
            return redirect('bankapp-account-list')
        except Exception as e:
            messages.error(request, str(e), extra_tags="danger")

    return render(
        request,
        'client/account/withdraw.html',
        {
            'form': form
        }
    )

@app_login_required()
def transfer(request):
    form = BankTransferForm(request.POST or None, user=request.user)

    if request.method == 'POST' and form.is_valid():
        source = form.cleaned_data['source_account']
        destination = form.cleaned_data['destination_account']
        amount = form.cleaned_data['amount']

        try:
            TransactionService.transfer(
                request.user,
                source,
                destination,
                amount
            )
            messages.success(request, "Virement réussi.")
            return redirect('bankapp-account-list')
        except Exception as e:
            messages.error(request, str(e), extra_tags="danger")

    return render(
        request,
        'client/account/transfer.html',
        {
            'form': form
        }
    )