from django.contrib import admin
from django.urls import path, include
from .views import auth as auth_views

urlpatterns = [
    path('', auth_views.home, name='client-home'),
    path('oops', auth_views.oops, name='client-oops'),
    
    path('auth/register', auth_views.register, name="client-auth-register"),
    path('auth/register/check', auth_views.register_to_validate, name="client-auth-register_to_validate"),
    path('auth/register/validate', auth_views.register_validate, name="client-auth-register_validate"),
    path('auth/register/check/err', auth_views.register_to_validate_error, name='client-auth-register_to_validate_err'),
    
    path('auth/login', auth_views.login, name="client-auth-login"),
    path('auth/login/otp', auth_views.login_otp, name='client-auth-login-otp'),
    
    path('auth/logout', auth_views.logout, name="client-auth-logout"),
    
    path('auth/password/reset', auth_views.reset_password, name="client-auth-reset-password"),
    path('auth/password/reset/check', auth_views.reset_password_check, name="client-auth-reset-password-check"),
    path('auth/password/reset/validate', auth_views.reset_password_validate, name="client-auth-reset-password-validate"),
    path('auth/password/reset/done', auth_views.reset_password_done, name="client-auth-reset-password-done"),
]
