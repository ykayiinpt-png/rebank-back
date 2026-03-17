from django.utils import timezone
from datetime import timedelta

from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _t
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from apps.core.helpers.mail import send_template_email
from apps.core.services.user_account import generate_registration_token, validate_registration_token

from .forms import UserRegisterForm, UserRegisterValidationForm

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
                
            
        
    return redirect("client-home")
 
@require_GET
def register_to_validate_error(request: HttpRequest):
    # Clear the session
    return render(request, 'client/auth/register_validate_err.html', {})
       
# [END] Registration

# [START] Login
# [END] Login

# [START] Recover Password
# [END] Recover Password

# [START] Change password
# [END] Change password
# [END] Authentication