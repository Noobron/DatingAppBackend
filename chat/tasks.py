from DatingAppBackend.celery import app
from dateutil import parser

from accounts.models import User

from chat.models import ChatMessage, ChatRoom


# Update db by running the celery task
@app.task
def update_chat_db(messages, username1, username2):

    user1 = User.objects.filter(username=username1).first()

    user2 = User.objects.filter(username=username2).first()

    if user1 is None or user2 is None:
        return

    if user1.username > user2.username:
        user1, user2 = user2, user1

    chat_room_name = user1.username + '_' + user2.username + '_chat'

    chat_room = ChatRoom.objects.filter(chat_room_name=chat_room_name).first()

    if chat_room is None:
        chat_room = ChatRoom(chat_room_name=chat_room_name,
                             user1=user1,
                             user2=user2)
        chat_room.save()

    last_chat_message = None

    for message in messages:
        message_type = None

        sender = None
        recipient = None

        created_at = None

        seen = None

        content = None

        try:
            if 'messageType' in message and type(
                    message['messageType']) == str:
                message_type = message['messageType'].lower()

            if 'sender' in message and type(message['sender']) == str:
                sender = user1 if user1.username.lower(
                ) == message['sender'].lower() else user2

            if 'recipient' in message and type(message['recipient']) == str:
                recipient = user1 if user1.username.lower(
                ) == message['recipient'].lower() else user2

            if 'createdAt' in message:
                created_at = parser.parse(message['createdAt'])

            if 'seen' in message:
                seen = True if message['seen'] else False

            if 'content' in message:
                content = message['content']

            chat_message = ChatMessage(message_type=message_type,
                                       sender=sender,
                                       recipient=recipient,
                                       created_at=created_at,
                                       seen=seen,
                                       content=content,
                                       chat_room=chat_room)

            chat_message.full_clean()

            chat_message.save()

            last_chat_message = chat_message

        except Exception as error:
            print(error)

    if last_chat_message is not None:
        chat_room.last_chat_message = last_chat_message
        chat_room.save()