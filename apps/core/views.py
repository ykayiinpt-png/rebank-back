import logging
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login as app_login
from django.utils.translation import gettext as _t
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from apps.core.helpers.mail import send_template_email
from apps.core.helpers.time import timestamp_has_expired
from apps.core.services.user_account import generate_registration_token, send_login_otp, validate_login_otp_signature, validate_registration_token

from .forms import UserLoginForm, UserLoginOtpForm, UserRegisterForm, UserRegisterValidationForm


logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'client/home.html', {})


# [START] Authentication
# [START] Registration
@require_http_methods(['GET', 'POST'])
def register(request: HttpRequest):
    form = None
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            UserModel = get_user_model()
            
            # Get data
            email = form.cleaned_data.get('email')
            
            # Validate user and email existence
            existing_user = UserModel.objects.filter(email=email).first()
            if existing_user is not None:
                # Check if user is active
                if existing_user.is_active:
                    # We return an error message
                    messages.error(request, _t("Ce compte existe déjà; veuillez vérifier votre email"))
                else:
                    # Check if we do have pass 1 hours since the first registration
                    if timezone.now() - existing_user.updated_at > timedelta(hours=1) :
                        # We resend the account registration validation email
                        existing_user.save() # We do this in order to have updated_at updated
                        
                        generate_registration_token(
                            email,
                            True
                        )
                        messages.success(request, _t("Enrégistrement Réussi Nous vous invitons à vérifier votre email"))
                    else:
                        # Call the user to check its email
                        messages.success(request, _t("Nous vous avions envoyé un mail de confirmation"))
            else:
                # Lutilisateur n'existe pas
                # on sauveagarde l'utilisateur et on lui envoi un mail
                form.save()
                
                generate_registration_token(
                    email, True
                )
                
                messages.success(request, _t("Enrégistrement Réussi Nous vous invitons à vérifier votre email"))
            
            return redirect('client-auth-register_to_validate')
    else:
        form = UserRegisterForm()
        
    # Render the page
    return render(
        request, 
        'client/auth/register.html', 
        {
            "form": form
        }
    )

@require_GET
def register_to_validate(request: HttpRequest):
    # Clear the session
    return render(request, 'client/auth/register_validate.html', {})

@require_GET
def register_validate(request: HttpRequest):
    form = UserRegisterValidationForm(request.GET)
    
    if form.is_valid():
        if validate_registration_token(form.cleaned_data['email'], form.cleaned_data['token']):
            UserModel = get_user_model()
            
            existing_user = UserModel.objects.filter(email=form.cleaned_data['email']).first()
            if existing_user is not None:
                # We activate the user account
                existing_user.is_active = True
                existing_user.save()
                
                send_template_email(
                    "Bienvenu(e) Chez Rebank",
                    "client_registration_validated",
                    { "email": existing_user.email },
                    existing_user.email
                )
                
                messages.success(request, _t("Validation du compte réussi"))
                # TODO: Go to Dashboard
            else:
                messages.error(request, _t("Votre lien est invalide"), extra_tags="danger")
                return redirect('client-auth-register_to_validate_err')
        else:
            messages.error(request, _t("Votre lien est invalide"), extra_tags="danger")
        
    return redirect("client-home")
 
@require_GET
def register_to_validate_error(request: HttpRequest):
    # Clear the session
    return render(request, 'client/auth/register_validate_err.html', {})
       
# [END] Registration

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
                # Generate otp and send by email
                id_token, otp_exp = send_login_otp(email, True)
                request.session['otp'] = { 'id_token': id_token, 'exp': otp_exp, 'email': email }
                
                # Redirect user to the otp page to enter otp
                return redirect('client-auth-login-otp')
            else:
                # Invalid credentials
                messages.error(request, _t("Vos identifiants sont incorrects"), extra_tags='danger')
    else:        
        form = UserLoginForm()
    
    return render(
        request,
        'client/auth/login.html',
        {
            'form': form
        }
    )

@require_http_methods(['GET', 'POST'])
def login_otp(request: HttpRequest):
    form = None
    
    if request.method == "POST":
        form = UserLoginOtpForm(request.POST)
        
        if form.is_valid():
            otp = form.cleaned_data['otp']
            
            if request.session and request.session.has_key("otp"):
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
                                app_login(request, user)
                                messages.success(request, _t("Vous êtes connecté."))
                                
                                # Everything went OK
                                return redirect('client-home')
                            else:
                                logger.error("User received OTP but does not exists")
                                
                                messages.error(_t("Veuillez réessayer"), extra_tags="danger")
                                
                                # The user will be reprompt the otp page
                    else:
                        messages.error(_t("Votre session a expirée"), extra_tags="danger")
                except Exception as e:
                    logger.error("User tried OTP: OTP Session is invalid")
                    messages.error(_t("Votre session a expirée"), extra_tags="danger")
                    pass
            else:
                messages.error(_t("Votre session a expirée"), extra_tags="danger")
                
                # Returns User to login screen
                return redirect('client-auth-login')
    else:
        form = UserLoginOtpForm()
        
    
    return render(
        request,
        'client/auth/login_otp.html',
        {
            'form': form
        }
    )
    
# [END] Login

# [START] Recover Password
# [END] Recover Password

# [START] Change password
# [END] Change password
# [END] Authentication