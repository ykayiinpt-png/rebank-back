from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.core.apis.views.auth import RegisterView
urlpatterns = [
    path('api/auth/register', RegisterView.as_view(), name="api-auth-register"),
     path('api/auth/login', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh_token', TokenRefreshView.as_view(), name='token_refresh'),
]
