from django.http import HttpRequest
from django.shortcuts import redirect
from functools import wraps

def app_login_required():
    """
    Login required in application
    """
    
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request: HttpRequest, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            return redirect('client-auth-login')
        return _wrapped_view
    return decorator