from re import I
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path
from django.core.asgi import get_asgi_application

import accounts.routing

from middlewares.token_authenticator import JwtTokenAuthMiddleware

application = ProtocolTypeRouter({
    'http':
    get_asgi_application(),
    'websocket':
    JwtTokenAuthMiddleware(URLRouter(accounts.routing.websocket_urlpatterns))
})
