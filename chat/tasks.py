from celery import shared_task
from channels.db import database_sync_to_async
from dateutil import parser

from chat.models import ChatMessage


# Update db by running the celery task
@shared_task
@database_sync_to_async
def update_chat_db(messages, user1, user2):
    for message in messages:
        message_type = None

        sender = None
        recipient = None

        created_at = None

        seen = None

        content = None

        try:
            if 'message_type' in message and type(
                    message['message_type']) == str:
                message_type = message['message_type'].lower()

            if 'sender' in message and type(message['sender']) == str:
                sender = user1 if user1.username.lower(
                ) == message['sender'] else user2

            if 'recipient' in message and type(message['recipient']) == str:
                recipient = user1 if user1.username.lower(
                ) == message['recipient'].lower() else user2

            if 'created_at' in message:
                created_at = parser.parse(message['created_at'])

            if 'seen' in message:
                seen = True if message['seen'] else False

            if 'content' in message:
                content = message['content']

            chat_room_name = min(user1.username, user2.username) + '_' + max(
                user1.username, user2.username) + '_chat'

            chat_message = ChatMessage(message_type=message_type,
                                       sender=sender,
                                       recipient=recipient,
                                       created_at=created_at,
                                       seen=seen,
                                       content=content,
                                       chat_room_name=chat_room_name)

            chat_message.full_clean()

            chat_message.save()

        except Exception as error:
            print(error)
