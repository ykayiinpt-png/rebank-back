from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """Limit login attempts to prevent brute force."""
    scope = 'login'

    def get_cache_key(self, request, view):
        # Throttle by IP + email combination
        email = request.data.get('email', '')
        ident = f"{self.get_ident(request)}_{email}"
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class OtpRateThrottle(SimpleRateThrottle):
    """Limit OTP verification attempts."""
    scope = 'otp'

    def get_cache_key(self, request, view):
        email = request.data.get('email', '')
        ident = f"{self.get_ident(request)}_{email}"
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class RegisterRateThrottle(SimpleRateThrottle):
    """Limit registration to prevent spam."""
    scope = 'register'

    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }
