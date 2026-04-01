from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.core.apis.views.auth import (
    LoginOtpView, RegisterOtpView, RegisterView, LoginView,
    ResetPasswordRequestView, ResetPasswordOtpView, ResetPasswordConfirmView
)

urlpatterns = [
    path('api/auth/register', RegisterView.as_view(), name="api-auth-register"),
    path('api/auth/register/otp', RegisterOtpView.as_view(), name='api-auth-register-otp'),
    path('api/auth/login', LoginView.as_view(), name='api-auth-login'),
    path('api/auth/login/otp', LoginOtpView.as_view(), name='api-auth-login-otp'),
    path('api/auth/password/reset', ResetPasswordRequestView.as_view(), name='api-auth-password-reset'),
    path('api/auth/password/reset/otp', ResetPasswordOtpView.as_view(), name='api-auth-password-reset-otp'),
    path('api/auth/password/reset/confirm', ResetPasswordConfirmView.as_view(), name='api-auth-password-reset-confirm'),
    path('api/auth/refresh_token', TokenRefreshView.as_view(), name='token_refresh'),
]
