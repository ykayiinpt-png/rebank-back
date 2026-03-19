from rest_framework.generics import CreateAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.translation import gettext as _t

from apps.core.apis.serializers.register import RegisterSerializer
from apps.core.services.auth import AuthService

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            
            print(request.data, serializer.data)
            
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
            raise e
            return Response({"message": str(e) }, status=status.HTTP_417_EXPECTATION_FAILED)
        
        
    