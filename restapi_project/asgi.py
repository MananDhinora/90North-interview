import os
import django  # Import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Set the correct DJANGO_SETTINGS_MODULE
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "restapi_project.settings"
)  # replace restapi_project with your project name.

# Initialize Django
django.setup()

from chat_app import routing  # import routing after django.setup()

# Initialize the ASGI application
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)),
    }
)

# For Vercel deployment
app = application
