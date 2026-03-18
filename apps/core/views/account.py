from django.http import HttpRequest
from django.shortcuts import render

from apps.core.decorators.auth import app_login_required


@app_login_required()
def dashboard(request: HttpRequest):
    """
    Tableau de board
    """
    
    context = {
        'account': 0,
        'transactions_count': 0
    }
    
    return render(request, 'client/account/dashboard.html', context)