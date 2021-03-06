from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import main.routing

ASGI_APPLICATION = "chattingapp.routing.application"
application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            main.routing.websocket_urlpatterns
        )
    ),
})