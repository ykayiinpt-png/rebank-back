from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('staff/auth/login', views.login, name="staff-auth-login"),
    path('staff/auth/login/otp', views.login_otp, name='staff-auth-login-otp'),
    
    path('staff/auth/logout', views.logout, name="staff-auth-logout"),
    
    # Account
    path('staff/dashboard', views.dashboard, name="staff-dashboard"),
    
    path('staff/accounts/list', views.list_accounts, name='staff-accounts-list'),
    path('staff/accounts/detail/<int:pk>', views.detail_account, name='staff-account-detail'),
    path('staff/accounts/validate/<int:pk>', views.validate_account, name='staff-account-validate'),
    path('staff/accounts/deposit/<int:pk>', views.deposit_account, name='staff-account-deposit')  ,
    
    path('staff/transactions/list', views.list_transactions, name='staff-transactions-list'),   
]
