import logging
from datetime import timedelta
import random

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login as app_login, logout as app_logout
from django.utils.translation import gettext as _t
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from apps.bankapp.forms.transaction import BankDepositForm
from apps.bankapp.models.account import BankAccount
from apps.bankapp.models.transaction import BankTransaction
from apps.bankapp.services.account import AccountService
from apps.core.forms import UserLoginForm, UserLoginOtpForm
from apps.core.helpers.time import timestamp_has_expired
from apps.core.models.auth import BaseUserSession
from apps.core.services.user_account import send_login_otp, validate_login_otp_signature
from apps.core.decorators.auth import app_login_staff_required


logger = logging.getLogger(__name__)

# [START] Login
@require_http_methods(['GET', 'POST'])
def login(request: HttpRequest):
    form = None
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # We make sure that we do not have a valid user session
                existing_login_session = BaseUserSession.objects.filter(
                    email=user.email, is_valid=True
                ).order_by('-created_at').first()
                
                # A valid and non expired login session
                if (existing_login_session is not None) and (not timestamp_has_expired(expiry_datetime=existing_login_session.exp)):
                    # A session exists and has not logged out yet
                    messages.error(
                        request,
                        _t("Une session d'utilisateur existe déjà. Veuillez vous déconnecter"),
                        extra_tags='danger'
                    )
                else:
                    # Generate otp and send by email
                    id_token, otp_exp = send_login_otp(email, True)
                    request.session['otp'] = { 'id_token': id_token, 'exp': otp_exp, 'email': email }
                    # Redirect user to the otp page to enter otp
                    return redirect('staff-auth-login-otp')
            else:
                # Invalid credentials
                messages.error(request, _t("Vos identifiants sont incorrects"), extra_tags='danger')
    else:        
        form = UserLoginForm()
    
    return render(
        request,
        'staff/auth/login.html',
        {
            'form': form
        }
    )

@require_http_methods(['GET', 'POST'])
def login_otp(request: HttpRequest):
    form = None
    
    if not (request.session and request.session.has_key("otp")):
        # If not otp has been set, we just redirect to the login page
        return redirect('staff-auth-login')
    
    if request.method == "POST":
        form = UserLoginOtpForm(request.POST)
        
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            try:
                if not timestamp_has_expired(request.session['otp']['exp']):
                    # We compare the signature
                    if validate_login_otp_signature(
                        request.session['otp']['email'], 
                        otp, request.session['otp']['id_token']):
                        # They are equal we log in the user
                        UserModel = get_user_model()
                        
                        user = UserModel.objects.filter(email=request.session['otp']['email']).first()
                        if user is not None:
                            # Save a new login session for the authenticated user
                            BaseUserSession.objects.create(
                                email=request.session['otp']['email'],
                                exp=timezone.now() + timedelta(minutes=settings.LOGIN_SESSION_EXPIRE_MINUTES)
                            )
                            
                            # Set expiration of the login session
                            request.session.set_expiry(timedelta(minutes=settings.LOGIN_SESSION_EXPIRE_MINUTES)) 
                            
                            # Login in the app
                            del request.session['otp']
                            request.session.modified = True
                            
                            app_login(request, user)
                            
                            messages.success(request, _t("Vous êtes connecté."))
                            
                            # Everything went OK
                            return redirect('staff-dashboard')
                        else:
                            logger.error("User received OTP but does not exists")
                            
                            messages.error(request, _t("Veuillez réessayer"), extra_tags="danger")
                            
                            return redirect('staff-auth-login')
                    else:
                        messages.error(request, _t("Votre otp est incorrect"), extra_tags="danger")
                else:
                    messages.error(request, _t("Votre session est expiré"), extra_tags="danger")
                    return redirect('staff-auth-login')
            except Exception as e:
                logger.error("User tried OTP: OTP Session is invalid")
                messages.error(request, _t("Votre session est expirée"), extra_tags="danger")
                return redirect('staff-auth-login')
                
    else:
        # We have a get request
        form = UserLoginOtpForm()
    
    return render(
        request,
        'staff/auth/login_otp.html',
        {
            'form': form
        }
    )
    
# [END] Login

# [START] Logout
@app_login_staff_required()
@require_POST
def logout(request: HttpRequest):
    if request.user.is_authenticated:
        # Delete all available sessions
        BaseUserSession.objects.filter(
            email=request.user.email, is_valid=True
        ).update(is_valid=False)
        
        logger.info(f'User {request.user.email} login session has been invalidated')
        
        tmp_email = request.user.email
         
        app_logout(request)
        
        logger.info(f'User {tmp_email} logged out')
    
    return redirect('staff-auth-login')

# [END] Logout



@app_login_staff_required()
@require_GET
def dashboard(request: HttpRequest):
    """
    Tableau de board
    """
    
    context = {
        'account': 0,
        'transactions_count': 0
    }
    
    return render(request, 'staff/account/dashboard.html', context)


@app_login_staff_required()
def list_accounts(request: HttpRequest):
    accounts = BankAccount.objects.all()
    
    return render(request, 'staff/account/accounts_list.html', {
        "accounts": accounts
    })
    
@require_GET
@app_login_staff_required()
def detail_account(request: HttpRequest, pk: int):
    """
    """
    
    account = BankAccount.objects.filter(pk=pk,).first()
    if account is None:
        messages.error(request, _t("Le compte bancaire n'existe pas"), extra_tags="danger")
        return redirect('staff-accounts-list')
        
    # List transactions
    historic_transactions = BankTransaction.objects.filter(
        Q(source_account=account) | Q(destination_account=account)
    ).order_by('-created_at').all()[:5]
    
    return render(
        request,
        'staff/account/detail.html',
        {
            "account": account,
            'historic_transactions': historic_transactions
        }
    )
    
@app_login_staff_required()
@require_POST
def validate_account(request: HttpRequest, pk: int):
    """
    """
    
    account = BankAccount.objects.filter(pk=pk,).first()
    if account is None:
        messages.error(request, _t("Le compte bancaire n'existe pas"), extra_tags="danger")
        return redirect('staff-accounts-list')
    
    account.approved = True
    account.approved_at = timezone.now()
    
    while True:
        numero = random.randint(0, 10000) + 1408909485989
        if BankAccount.objects.filter(numero=numero).first() is None:
            account.numero = numero
            break
    
    account.save()
    
    return redirect('staff-accounts-list')

@app_login_staff_required()
@require_GET
def list_transactions(request: HttpRequest):
    transactions = BankTransaction.objects.all().order_by('-created_at').all()
    return render(
        request,
        'staff/account/transactions_list.html',
        {
            "transactions": transactions
        }
    )
    
    

@app_login_staff_required()
@require_http_methods(["GET", "POST"])
def deposit_account(request: HttpRequest, pk: int):
    account = BankAccount.objects.filter(pk=pk, approved=True).first()
    if account is None:
        messages.error(request, _t("Le compte bancaire n'existe pas"), extra_tags="danger")
        return redirect('staff-accounts-list')
    
    
    if request.method == "POST":
        form = BankDepositForm(request.POST, user=None, accounts=[account])
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            if amount <= 0:
                messages.error(request, _t("Le montant doit être positif."), extra_tags="danger")
            else:
                # Lock the row
                account = BankAccount.objects.select_for_update().filter(pk=pk).first()

                account.balance += amount
                account.save()

                BankTransaction.objects.create(
                    user=account.user,
                    transaction_type='DEPOSIT',
                    amount=amount,
                    destination_account=account,
                    status='COMPLETED',
                    balance_after=account.balance
                ), None
                
                messages.success(request, _t(f"Vous venez de faire un dépôt sur le compte {account.numero}"))
                
                return redirect('staff-accounts-list')
    else:
        form = BankDepositForm(user=None, accounts=[account])
        
    return render(
        request,
        "staff/account/deposit.html",
        {
            "form": form
        }
    )