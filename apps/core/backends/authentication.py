from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Email based authentication. Remenber just authentication
    """
    

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email") or username

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None

        salted_password = password + user.salt
    
        if user.check_password(salted_password):
            return user

        return None