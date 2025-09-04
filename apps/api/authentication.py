from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ApiClient

class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class for API key validation.
    Authenticates against the `X-API-Key` header.
    """
    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None # No API key provided

        try:
            api_client = ApiClient.objects.get(api_key=api_key, is_active=True)
        except ApiClient.DoesNotExist:
            raise AuthenticationFailed('Invalid API Key or Inactive Client')

        return (api_client.user, None) # Return user and no auth token

    def authenticate_header(self, request):
        return 'X-API-Key'
