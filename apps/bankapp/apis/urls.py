from django.urls import path

from apps.bankapp.apis.views.account import BankAccountCreateView, BankAccountDetailView, BankAccountListView, BankAccountUpdateView
from apps.bankapp.apis.views.transactions import BankDepositAPIView, BankTransactionListAPIView, BankTransferAPIView, BankWithdrawAPIView, RecentContactsAPIView

urlpatterns = [
    path('api/accounts/', BankAccountCreateView.as_view(), name='bankap-api-account-create'),
    path('api/accounts/list', BankAccountListView.as_view(), name='bankap-api-account-list'),
    path('api/accounts/<int:pk>/', BankAccountDetailView.as_view(), name='bankap-api-account-detail'),
    path('api/accounts/<int:pk>/update/', BankAccountUpdateView.as_view(), name='bankap-api-account-update'),

    path('api/transactions/deposit', BankDepositAPIView.as_view()),
    path('api/transactions/withdraw', BankWithdrawAPIView.as_view()),
    path('api/transactions/transfer', BankTransferAPIView.as_view()),
    path('api/transactions/list', BankTransactionListAPIView.as_view()),
    path('api/contacts/recent', RecentContactsAPIView.as_view()),
]