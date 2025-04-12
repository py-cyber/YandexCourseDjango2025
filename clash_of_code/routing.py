from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import duet.routing


application = ProtocolTypeRouter(
    {
        'websocket': AuthMiddlewareStack(URLRouter(duet.routing.websocket_urlpatterns)),
    },
)
