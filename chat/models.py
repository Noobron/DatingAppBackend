from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import CICharField

from accounts.models import User

# types of chat messages available
TEXT = 'text'

MESSAGE_TYPE = [
    (TEXT, _('Chat message type : Text')),
]


class ChatRoom(models.Model):
    """
    Class for chat rooms
    """

    # name of the chat room to which the message belongs to
    chat_room_name = CICharField(
        max_length=125,
        unique=True,
        null=False,
        blank=False,
    )

    # last message of the chat room
    last_chat_message = models.ForeignKey('ChatMessage',
                                          on_delete=models.CASCADE,
                                          null=True)


class ChatMessage(models.Model):
    """
    Class for storing chat messages between `Users`
    """

    # type of the message
    message_type = models.CharField(choices=MESSAGE_TYPE,
                                    max_length=50,
                                    null=False,
                                    blank=False)

    # user who created the text message
    sender = models.ForeignKey(User,
                               related_name='sender',
                               on_delete=models.CASCADE,
                               null=False)

    # user who is supposed to receive the message
    recipient = models.ForeignKey(User,
                                  related_name='recipient',
                                  on_delete=models.CASCADE,
                                  null=False)

    # timestamp at which the message was created
    created_at = models.DateTimeField(default=timezone.now)

    # whether the recipient has seen the message
    seen = models.BooleanField(default=False)

    # content of the chat message
    content = models.TextField(null=False, blank=False)

    # chat room of the chat message
    chat_room = models.ForeignKey(ChatRoom,
                                  related_name='chat_room',
                                  null=False,
                                  on_delete=models.CASCADE)
