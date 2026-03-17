from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='client-home'),
    path('auth/register', views.register, name="client-auth-register"),
    path('auth/register/check', views.register_to_validate, name="client-auth-register_to_validate"),
    path('auth/register/validate', views.register_validate, name="client-auth-register_validate"),
    path('auth/register/check/err', views.register_to_validate_error, name='client-auth-register_to_validate_err')
]
