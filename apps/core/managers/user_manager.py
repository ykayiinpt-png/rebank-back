from django.contrib.auth.models import BaseUserManager

class AppBaseUserManager(BaseUserManager):
    
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        user = self.model(email=email, username=email,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        print("In create user of the manager")
        
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        """
        Override this method to normalize the email input
        before attempting to find the user in the database.
        """
        email = self.normalize_email(username)
        return self.get(**{self.model.USERNAME_FIELD: email})