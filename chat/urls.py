from django.urls import path

from . import views

urlpatterns = [
    path('get-chat-messages/',
         views.get_chat_messages,
         name='get_chat_messages'),
    path('mark-chat-message-as-seen/',
         views.mark_chat_message_as_seen,
         name='mark_chat_message_as_seen'),
    path('get-chat-feed/', views.get_chat_feed, name='get_chat_feed')
]