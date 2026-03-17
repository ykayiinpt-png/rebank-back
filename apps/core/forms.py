from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _t
from django import forms

from apps.core.models.base_user import BaseUser

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email"
    )
    
    class Meta:
        model = get_user_model()
        fields=('email',)
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = _t("Entrez le même mot de passe que précédemment, à des fins de vérification.")
        
    def validate_unique(self):
        exclude = self._get_validation_exclusions()
        exclude.add('email')
        self.instance.validate_unique(exclude=exclude)

class UserRegisterValidationForm(forms.Form):
    email = forms.EmailField(required=True)
    token = forms.CharField(required=True)

class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    

class UserLoginOtpForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6, required=True)