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
    _content = models.TextField(null=False, blank=False, db_column="content")

    # name of the chat room to which the message belongs to
    chat_room_name = CICharField(
        max_length=125,
        null=False,
        blank=False,
    )

    @property
    def content(self):
        return self._content

    def process_content(self, data):
        # default is TEXT

        if self.message_type == TEXT:
            return data
        else:
            return data

    @content.setter
    def content(self, data):
        self._content = self.process_content(data)
