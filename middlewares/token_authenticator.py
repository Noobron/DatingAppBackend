from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
import jwt

from accounts.models import User

from DatingAppBackend import settings


@database_sync_to_async
def get_user(user_id):
    user = User.objects.filter(id=user_id).first()
    return user if user is not None and user.is_active else AnonymousUser()


class JwtTokenAuthMiddleware(BaseMiddleware):
    """
    Custom JWT Token Authentocation for Web Sockets
    """
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            query_params = parse_qs(scope['query_string'].decode())

            access_token = query_params['access_token'][-1]

            user_id = jwt.decode(access_token,
                                 settings.SECRET_KEY,
                                 algorithms=['HS256'])['user_id']
        except:
            user_id = None

        scope['user'] = AnonymousUser() if user_id is None else await get_user(
            user_id)

        return await super().__call__(scope, receive, send)