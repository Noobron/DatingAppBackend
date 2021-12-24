from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user_name_1>\w+)_(?P<user_name_2>\w+)_chat/$',
            consumers.ChatConsumer.as_asgi())
]