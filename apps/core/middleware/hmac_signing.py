import hmac
import hashlib
import time
import logging

from django.conf import settings
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Requests older than 5 minutes are rejected (replay attack protection)
HMAC_MAX_AGE_SECONDS = 300


class HmacSignatureMiddleware:
    """
    Middleware that verifies HMAC-SHA256 signatures on API requests.

    The client must send:
      X-Timestamp: Unix timestamp (seconds)
      X-Signature: HMAC-SHA256(secret, "timestamp.method.path.body_hash")

    Only applies to /api/ endpoints (excluding docs & auth endpoints that
    are called before the client has established a session).
    """

    # Endpoints that don't require HMAC (pre-auth flows)
    EXEMPT_PREFIXES = (
        '/api/docs',
        '/api/schema',
        '/api/auth/login',
        '/api/auth/register',
        '/api/auth/password/reset',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce on API endpoints
        if request.path.startswith('/api/') and not self._is_exempt(request.path):
            error = self._verify_signature(request)
            if error:
                return JsonResponse({'message': error}, status=403)

        return self.get_response(request)

    def _is_exempt(self, path):
        return any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES)

    def _verify_signature(self, request):
        timestamp = request.META.get('HTTP_X_TIMESTAMP', '')
        signature = request.META.get('HTTP_X_SIGNATURE', '')

        if not timestamp or not signature:
            return 'Missing HMAC signature headers'

        # Verify timestamp freshness (anti-replay)
        try:
            ts = int(timestamp)
        except (ValueError, TypeError):
            return 'Invalid timestamp'

        now = int(time.time())
        if abs(now - ts) > HMAC_MAX_AGE_SECONDS:
            return 'Request timestamp expired'

        # Build the message to sign: "timestamp.METHOD.path.body_sha256"
        body = request.body or b''
        body_hash = hashlib.sha256(body).hexdigest()
        message = f"{timestamp}.{request.method}.{request.path}.{body_hash}"

        expected = hmac.new(
            settings.HMAC_API_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected):
            logger.warning(f'HMAC signature mismatch for {request.method} {request.path}')
            return 'Invalid HMAC signature'

        return None
