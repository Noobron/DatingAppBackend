from re import I
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from django.core.asgi import get_asgi_application

import accounts.routing

import chat.routing

from middlewares.token_authenticator import JwtTokenAuthMiddleware

websocket_urlpatterns = accounts.routing.websocket_urlpatterns
websocket_urlpatterns += chat.routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    'http':
    get_asgi_application(),
    'websocket':
    JwtTokenAuthMiddleware(URLRouter(websocket_urlpatterns))
})
