from django.urls import path

from .views import account as account_views
from .views import transaction as transaction_views

from .apis.urls import urlpatterns as api_urls

urlpatterns = [
    path('account/create', account_views.create_account, name='bankapp-account-create'),
    path('account/edit/<int:pk>', account_views.update_account, name='bankapp-account-update'),
    path('account/detail/<int:pk>', account_views.detail_account, name='bankapp-account-detail'),
    path('account/list', account_views.list_accounts, name='bankapp-account-list'),
    
    path('account/deposit', transaction_views.deposit, name='bankapp-account-deposit'),
    path('account/withdraw', transaction_views.withdraw, name='bankapp-account-withdraw'),
    path('account/transfer', transaction_views.transfer, name='bankapp-account-transfer'),
    
    path('account/transactions/list', transaction_views.list_transactions, name='bankapp-account-list-transactions'),
] + api_urls
