import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import apps.api.routing

# Set the default settings module for the 'asgi' program.
# It's crucial this points to your production settings in the deployed environment.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applaude_api.settings.production')

# Initialize Django application
django.setup()

# The default ASGI application for standard HTTP requests
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            apps.api.routing.websocket_urlpatterns
        )
    ),
})