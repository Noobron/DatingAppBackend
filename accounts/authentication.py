from django.http.response import HttpResponse
from rest_framework.exceptions import NotAuthenticated, NotFound
from rest_framework import authentication
import jwt

from DatingAppBackend import settings

from accounts.models import User


class CustomAuthentication(authentication.BaseAuthentication):
    """
    Custom JWT Authentication class to set current user if authenticated otherwise set user as Anonymous
    """

    def authenticate(self, request):

        authorization_header = request.headers.get('Authorization')

        if not authorization_header:
            return None
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(access_token,
                                 settings.SECRET_KEY,
                                 algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return None
        except IndexError:
            return None
        except jwt.InvalidSignatureError:
            return None
        except jwt.DecodeError:
            return None
        except Exception as e:
            raise NotAuthenticated(e)

        user = User.objects.filter(id=payload['user_id']).first()

        if user is None:
            raise NotFound('User not found')

        if not user.is_active:
            raise NotAuthenticated('User is inactive')

        return (user, None)
