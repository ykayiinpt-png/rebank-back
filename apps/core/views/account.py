from django.http import HttpRequest
from django.shortcuts import render
from django.db.models import Q

from apps.core.decorators.auth import app_login_required
from apps.bankapp.models.account import BankAccount
from apps.bankapp.models.transaction import BankTransaction


@app_login_required()
def dashboard(request: HttpRequest):
    accounts_count = BankAccount.objects.filter(user=request.user).count()
    transactions_count = BankTransaction.objects.filter(
        Q(source_account__user=request.user) | Q(destination_account__user=request.user)
    ).count()

    context = {
        'account': accounts_count,
        'transactions_count': transactions_count,
    }
    return render(request, 'client/account/dashboard.html', context)
