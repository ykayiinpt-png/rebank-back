from django.urls import path

from .views import account as account_views

urlpatterns = [
    path('account/create', account_views.create_account, name='bankapp-account-create'),
    path('account/list', account_views.list_accounts, name='bankapp-account-list')
]
