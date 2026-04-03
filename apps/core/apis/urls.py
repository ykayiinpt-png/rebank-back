from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.core.apis.views.auth import (
    LoginOtpView, LogoutView, RegisterOtpView, RegisterView, LoginView,
    ResetPasswordRequestView, ResetPasswordOtpView, ResetPasswordConfirmView,
    TwoFactorToggleView, UserProfileView,
)

urlpatterns = [
    path('api/auth/register', RegisterView.as_view(), name="api-auth-register"),
    path('api/auth/register/otp', RegisterOtpView.as_view(), name='api-auth-register-otp'),
    path('api/auth/login', LoginView.as_view(), name='api-auth-login'),
    path('api/auth/login/otp', LoginOtpView.as_view(), name='api-auth-login-otp'),
    path('api/auth/logout', LogoutView.as_view(), name='api-auth-logout'),
    path('api/auth/password/reset', ResetPasswordRequestView.as_view(), name='api-auth-password-reset'),
    path('api/auth/password/reset/otp', ResetPasswordOtpView.as_view(), name='api-auth-password-reset-otp'),
    path('api/auth/password/reset/confirm', ResetPasswordConfirmView.as_view(), name='api-auth-password-reset-confirm'),
    path('api/auth/refresh_token', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/2fa/toggle', TwoFactorToggleView.as_view(), name='api-auth-2fa-toggle'),
    path('api/auth/profile', UserProfileView.as_view(), name='api-auth-profile'),
]
