import datetime
import logging
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login as app_login, logout as app_logout
from django.utils.translation import gettext as _t
from django.utils import timezone
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from apps.core.helpers.mail import send_template_email
from apps.core.helpers.time import timestamp_has_expired
from apps.core.models.auth import BaseUserSession
from apps.core.services.user_account import generate_registration_token, generate_reset_password_token, send_login_otp, validate_login_otp_signature, validate_registration_token, validate_reset_password_token

from ..forms import UserLoginForm, UserLoginOtpForm, UserRecoverPassword, UserRecoverPasswordSet, UserRecoverPasswordValidate, UserRegisterForm, UserRegisterValidationForm


logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'client/home.html', {})

def oops(request):
    # TODO: add a guard here to have a session value before and clean before rendering the page
    return render(request, 'client/oops.html', {})


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
    
    if not (request.session and request.session.has_key("otp")):
        # If not otp has been set, we just redirect to the login page
        return redirect('client-auth-login')
    
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
                            
                            app_login(request, user, settings.AUTHENTICATION_BACKENDS[0])
                            
                            messages.success(request, _t("Vous êtes connecté."))
                            
                            # Everything went OK
                            return redirect('client-account-dashboard')
                        else:
                            logger.error("User received OTP but does not exists")
                            
                            messages.error(_t("Veuillez réessayer"), extra_tags="danger")
                            
                            # The user will be reprompt the otp page
                else:
                    messages.error(_t("Votre session est expiré"), extra_tags="danger")
            except Exception as e:
                logger.error("User tried OTP: OTP Session is invalid")
                messages.error(_t("Votre session est expirée"), extra_tags="danger")
                
    else:
        # We have a get request
        form = UserLoginOtpForm()
        
    
    return render(
        request,
        'client/auth/login_otp.html',
        {
            'form': form
        }
    )
    
# [END] Login

# [START] Logout
@require_POST
def logout(request: HttpRequest):
    if request.user.is_authenticated:
        # Delete all available sessions
        BaseUserSession.objects.filter(
            email=request.user.email, is_valid=True
        ).update(is_valid=False)
        
        logger.info(f'User {request.user.email} login session has been invalidated')
        
        app_logout(request)
        
        logger.info(f'User {request.user.email} logged out')
    
    return redirect('client-home')

# [END] Logout

# [START] Recover Password
@require_http_methods(["POST", "GET"])
def reset_password(request: HttpRequest):
    form = None
    
    # TODO: avoid logged user
    
    if request.method == "POST":
        form = UserRecoverPassword(request.POST)
        
        if form.is_valid():
            UserModel = get_user_model()
            
            existing_user = UserModel.objects.filter(email=form.cleaned_data['email']).first()
            if (existing_user is not None) and (existing_user.is_active == True):
                generate_reset_password_token(existing_user.email, True)
                
                # Set a reset password flag.
                # Just to allow the user to see a page
                request.session['r_password'] = True
                
                messages.success(request, _t('Un mail a été envoyé pour validation'))
                
                return redirect('client-auth-reset-password-check')
            else:
                messages.error(_t("Veuillez fourni un email valid"))
    else:
        form = UserRecoverPassword()
        
    return render(
        request,
        'client/auth/reset_password.html',
        {
            'form': form
        }
    )
    
@require_http_methods(["POST", "GET"])
def reset_password_check(request: HttpRequest):
    """
    It shows a success message to the user and invite him to check upon
    his mails
    """
    
    # TODO: avoid logged user
    
    # Only allow if has visited the reset page
    if not request.session.has_key('r_password'):
        logger.warn('User trying to access reset password check page without visiting reset password page')
        return redirect('client-home')
    
    return render(request, 'client/auth/reset_password_check.html', {})

@require_http_methods(["POST", "GET"])
def reset_password_validate(request: HttpRequest):
    """
    Validate the password link by a GET method then provide the password
    update form to the user to submit by POST method
    """
    
    # TODO: avoid logged user
    
    if request.method == "GET":
        form = UserRecoverPasswordValidate(request.GET)
        if form.is_valid():
            if validate_reset_password_token(
                form.cleaned_data['email'],
                form.cleaned_data['exp'], form.cleaned_data['token']):
                
                # We set the session and provide the password update form to the user
                request.session['r_password'] = {'email': form.cleaned_data['email']}
                
                return render(
                    request,
                    'client/auth/reset_password_set.html',
                    {
                        'form': UserRecoverPasswordSet()
                    }
                )
            else:
                messages.error(request, _t('Votre lien est incorrect'), extra_tags='danger')
                return redirect('client-oops')
        else:
            messages.error(request, _t('Votre lien est incorrect'), extra_tags='danger')
            return redirect('client-oops')
    else:
        # Protection
        if not request.session.has_key('r_password'):
            messages.error(request, _t('Votre requete est in valide'), extra_tags='danger')
            return redirect('client-oops')
        
        form = UserRecoverPasswordSet(request.POST)
        if form.is_valid():
            UserModel = get_user_model()
            
            existing_user = UserModel.objects.filter(email=request.session['r_password']['email']).first()
            if existing_user:
                existing_user.set_password(form.cleaned_data['password'])
                existing_user.save()
                
                send_template_email(
                    "Mot de passe Initialisé",
                    "client_reset_password_done",
                    { },
                    existing_user.email
                )
                
                messages.success(request, _t('Mot de passe mis à jour'))
                
                # Redirect the sucess message
                return redirect('client-auth-reset-password-done')
        
        return render(
            request,
            'client/auth/reset_password_set.html',
            {
                'form': UserRecoverPasswordSet()
            }
        )
        
@require_GET
def reset_password_done(request: HttpRequest):
    """
    It shows a success message when password has been successfully updated
    """
    
    # TODO: avoid logged user
    
    # Only allow if has visited the reset page
    if not request.session.has_key('r_password'):
        logger.warn('User trying to access reset password check page without visiting reset password page')
        return redirect('client-home')
    
    # Clear the reset password flag
    del request.session['r_password']
    request.session.modified = True
    
    return render(request, 'client/auth/reset_password_done.html', {})
# [END] Recover Password

# [START] Change password
# [END] Change password
# [END] Authentication