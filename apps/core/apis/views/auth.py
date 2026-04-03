from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework import serializers as drf_serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext as _t
from django.core.exceptions import ValidationError
from apps.core.models.auth import BaseUserSession
from apps.core.throttles import LoginRateThrottle, OtpRateThrottle, RegisterRateThrottle
from drf_spectacular.utils import extend_schema, inline_serializer

from apps.core.apis.serializers.login import LoginOtpSerializer, LoginResponseSerializer, LoginSerializer, LoginTokensSerializer
from apps.core.apis.serializers.register import RegisterOtpSerializer, RegisterResponseSerializer, RegisterSerializer
from apps.core.apis.serializers.reset_password import (
    ResetPasswordRequestSerializer, ResetPasswordRequestResponseSerializer,
    ResetPasswordOtpSerializer, ResetPasswordOtpResponseSerializer,
    ResetPasswordConfirmSerializer
)
from apps.core.services.auth import AuthService


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    throttle_classes = [RegisterRateThrottle]

    @extend_schema(request=RegisterSerializer, responses={201: RegisterResponseSerializer})
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            _, id_token, otp_exp, verification_sent, verification_resent, check_email = AuthService.register_user(
                serializer.data['email'], serializer.data['password'], use_otp=True
            )

            message = ""
            if verification_sent:
                message = _t("Enrégistrement Réussi. Un code OTP a été envoyé à votre email")
            elif verification_resent:
                message = _t("Code OTP renvoyé. Veuillez vérifier votre email")
            elif check_email:
                message = _t("Nous vous avions envoyé un code de confirmation")

            response_data = {"message": message}
            if id_token and otp_exp:
                response_data["id_token"] = id_token
                response_data["otp_exp"] = otp_exp

            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            message = str(e)
            if isinstance(e, ValidationError):
                message = e.message
            return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)


class RegisterOtpView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [OtpRateThrottle]

    @extend_schema(request=RegisterOtpSerializer, responses={200: inline_serializer(
        name='RegisterOtpResponse',
        fields={'message': drf_serializers.CharField()}
    )})
    def post(self, request, *args, **kwargs):
        serializer = RegisterOtpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                AuthService.register_verify_otp(
                    serializer.validated_data['id_token'],
                    serializer.validated_data['otp'],
                    serializer.validated_data['otp_exp'],
                    serializer.validated_data['email'],
                )
                return Response(
                    {"message": _t("Compte vérifié avec succès. Vous pouvez maintenant vous connecter")},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        

class LoginView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [LoginRateThrottle]

    @extend_schema(request=LoginSerializer, responses={200: LoginResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                id_token, otp_exp = AuthService.login_user(serializer.validated_data['email'], serializer.validated_data['password'])
                
                return Response({ "id_token": id_token, "otp_exp": otp_exp })
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginOtpView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [OtpRateThrottle]

    @extend_schema(request=LoginOtpSerializer, responses={
        200: LoginTokensSerializer
    })
    def post(self, request, *args, **kwargs):
        serializer = LoginOtpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = AuthService.login_user_otp(
                    serializer.validated_data['id_token'], serializer.validated_data['otp'],
                    serializer.validated_data['otp_exp'], serializer.validated_data['email']
                )
                
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token)
                    }
                )
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(responses={200: inline_serializer(
        name='LogoutResponse',
        fields={'message': drf_serializers.CharField()}
    )})
    def post(self, request, *args, **kwargs):
        # Invalidate all active sessions for this user
        BaseUserSession.objects.filter(
            email=request.user.email, is_valid=True
        ).update(is_valid=False)

        return Response({"message": _t("Déconnexion réussie")})


class ResetPasswordRequestView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [LoginRateThrottle]

    @extend_schema(request=ResetPasswordRequestSerializer, responses={200: ResetPasswordRequestResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                id_token, otp_exp = AuthService.reset_password_request(
                    serializer.validated_data['email']
                )
                return Response({
                    "id_token": id_token,
                    "otp_exp": otp_exp,
                    "message": _t("Un code OTP a été envoyé à votre email")
                })
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordOtpView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [OtpRateThrottle]

    @extend_schema(request=ResetPasswordOtpSerializer, responses={200: ResetPasswordOtpResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordOtpSerializer(data=request.data)
        if serializer.is_valid():
            try:
                reset_token, reset_exp = AuthService.reset_password_verify_otp(
                    serializer.validated_data['id_token'],
                    serializer.validated_data['otp'],
                    serializer.validated_data['otp_exp'],
                    serializer.validated_data['email'],
                )
                return Response({
                    "reset_token": reset_token,
                    "reset_exp": reset_exp,
                })
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirmView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(request=ResetPasswordConfirmSerializer, responses={200: inline_serializer(
        name='ResetPasswordConfirmResponse',
        fields={'message': drf_serializers.CharField()}
    )})
    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                AuthService.reset_password_confirm(
                    serializer.validated_data['reset_token'],
                    serializer.validated_data['reset_exp'],
                    serializer.validated_data['email'],
                    serializer.validated_data['new_password'],
                )
                return Response({
                    "message": _t("Mot de passe réinitialisé avec succès")
                })
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)