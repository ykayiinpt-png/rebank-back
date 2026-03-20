from django.contrib import admin
from django.contrib.auth import get_user_model

from apps.core.forms import UserRegisterForm
from apps.core.models.auth import BaseUserSession

# Register your models here.
CustomUser = get_user_model()

class BankUserAdmin(admin.ModelAdmin):
    add_form = UserRegisterForm
    model = CustomUser
    
    def save_form(self, request, form, change):
        if not change:
            form.instance = CustomUser.objects.create_user(
                form.cleaned_data["email"],
                form.cleaned_data["password"],
                #**form.cleaned_data
            )
        return super().save_form(request, form, change)

class BankUserSessionAdmin(admin.ModelAdmin):
    model = BaseUserSession
    
    def has_delete_permission(self, request, obj = ...):
        if request.user.is_superuser:
            return True
        return False


admin.site.register(CustomUser, BankUserAdmin)
admin.site.register(BaseUserSession, BankUserSessionAdmin)