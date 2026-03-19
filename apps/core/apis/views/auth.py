from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext as _t
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, inline_serializer

from apps.core.apis.serializers.login import LoginOtpSerializer, LoginResponseSerializer, LoginSerializer, LoginTokensSerializer
from apps.core.apis.serializers.register import RegisterSerializer
from apps.core.services.auth import AuthService

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            _, verification_sent, verification_resent, check_email = AuthService.register_user(
                serializer.data['email'], serializer.data['password']
            )
            
            message = ""
            if verification_sent:
                message = _t("Enrégistrement Réussi Nous vous invitons à vérifier votre email")
            elif verification_resent:
                message = _t("Email Renvoyé. Nous vous invitons à vérifier votre email")
            elif check_email:
                message = _t("Nous vous avions envoyé un mail de confirmation")
            
            return Response({"message": message}, status=status.HTTP_201_CREATED)
        except Exception as e:
            message = str(e)
            if isinstance(e, ValidationError):
                message = e.message
            return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)
        
        

class LoginView(APIView):
    
    @extend_schema(request=LoginSerializer, responses={200: LoginResponseSerializer})
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            try:
                id_token, otp_exp = AuthService.login_user(serializer.validated_data['email'], serializer.validated_data['email'])
                
                return Response({ "id_token": id_token, "otp_exp": otp_exp })
            except Exception as e:
                message = str(e)
                if isinstance(e, ValidationError):
                    message = e.message
                return Response({"message": message}, status=status.HTTP_417_EXPECTATION_FAILED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginOtpView(APIView):
    
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