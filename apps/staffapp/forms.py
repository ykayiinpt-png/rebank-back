from django import forms

class UserLoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)
    

class UserLoginOtpForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6, required=True)