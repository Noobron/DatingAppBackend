import re
from caches import Cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser

from accounts.models import User

from DatingAppBackend import settings

from .tasks import update_chat_db


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer to handle real time chat between Users
    """
    def __init__(self):
        self.chat_device_count_cache = Cache("redis://" + settings.REDIS_HOST)
        self.chat_messages_cache = Cache("redis://" + settings.REDIS_HOST)
        super().__init__()

    # Get the valid User from database
    @database_sync_to_async
    def get_user(self, username):
        user = User.objects.filter(username=username).first()

        if user is not None and user.is_active:
            return user
        else:
            return AnonymousUser

    # Sync chat with the database by running a Celery task
    async def sync_chat_with_database(self):
        messages = await self.chat_messages_cache.get(self.chat_message_store)

        if messages is not None and len(messages) > 0:
            update_chat_db.delay(messages, self.channel_user.username,
                                 self.other_user.username)

        await self.chat_messages_cache.delete(self.chat_message_store)

    # Sync client with other devices if any
    async def sync_client(self):
        messages = await self.chat_messages_cache.get(self.chat_message_store)

        updates = False

        if messages is not None:
            for message in messages:

                if 'recipient' in message and self.channel_user.username.lower() == message['recipient'].lower() \
                    and 'seen' in message and message['seen'] == False:
                    message['seen'] = True

                    updates = True

                await self.channel_layer.group_send(self.personal_group, {
                    'type': 'message',
                    'content': message
                })

        if updates == True:
            await self.chat_messages_cache.set(self.chat_message_store,
                                               messages)

    # Add current client's device to the chat room
    async def add_device(self):

        count = await self.chat_device_count_cache.get(self.chat_device_count)

        if count is None:
            await self.chat_device_count_cache.set(self.chat_device_count, 1)
        else:
            await self.chat_device_count_cache.set(self.chat_device_count,
                                                   count + 1)

    # Remove current client's device from the chat room and sync the chat with database if no user belonging to the chat room is online
    async def remove_device(self):

        count = await self.chat_device_count_cache.get(self.chat_device_count)

        if count is not None:
            if count <= 1:
                await self.chat_device_count_cache.delete(
                    self.chat_device_count)

                await self.sync_chat_with_database()

            else:
                await self.chat_device_count_cache.set(self.chat_device_count,
                                                       count - 1)

    # Send message to group and update message store on receiving message from client
    async def receive(self, text_data=None, bytes_data=None):

        if text_data is not None:

            data_json = json.loads(text_data)

            content = data_json['data']

            if 'recipient' in content and self.channel_user.username.lower() == content['recipient'].lower() \
                    and 'seen' in content and content['seen'] == False:
                content['seen'] = True

            await self.channel_layer.group_send(self.chat_room_name, {
                'type': 'message',
                'content': content
            })

            messages = await self.chat_messages_cache.get(
                self.chat_message_store)

            if messages is None:
                messages = []

            messages.append(content)

            await self.chat_messages_cache.set(self.chat_message_store,
                                               messages)

    async def message(self, event):
        content = event['content']

        await self.send(text_data=json.dumps({
            'type': 'message',
            'content': content
        }))

    async def reject_connection(self, event):
        reject_message = event['reject_message']

        await self.send(text_data=json.dumps({
            'type': 'reject',
            'reject_message': reject_message
        }))

    async def accept_connection(self, event):
        accept_message = event['accept_message']

        await self.send(text_data=json.dumps({
            'type': 'accept',
            'accept_message': accept_message
        }))

    # Try connecting the client to the chat room
    async def connect(self):

        user_name_1 = self.scope['url_route']['kwargs']['user_name_1'].lower()

        user_name_2 = self.scope['url_route']['kwargs']['user_name_2'].lower()

        # Group specific for the channel to send synced messages or connection result back to the client
        self.personal_group = re.sub(r'[^0-9a-zA-Z]+', '-',
                                     self.channel_name) + "_personal_group"

        await self.channel_layer.group_add(self.personal_group,
                                           self.channel_name)

        await self.accept()

        if self.scope['user'] != AnonymousUser and \
            self.scope['user'].username.lower() == user_name_1 or self.scope['user'].username.lower() == user_name_2:

            self.channel_user = self.scope['user']

            if user_name_2 == self.scope['user'].username.lower():
                user_name_2 = user_name_1

            self.other_user = await self.get_user(user_name_2)

            if self.other_user == AnonymousUser:
                await self.channel_layer.group_send(
                    self.personal_group, {
                        'type': 'reject_connection',
                        'reject_message': 'connection refused'
                    })

                await self.channel_layer.group_discard(self.personal_group,
                                                       self.channel_name)
                return

            await self.channel_layer.group_send(
                self.personal_group, {
                    'type': 'accept_connection',
                    'accept_message': 'connection accepted'
                })

            self.chat_room_name = min(self.channel_user.username,
                                      self.other_user.username) + '_' + max(
                                          self.channel_user.username,
                                          self.other_user.username)

            self.chat_device_count = self.chat_room_name + '_device_count'

            self.chat_message_store = self.chat_room_name + '_message_store'

            await self.chat_messages_cache.connect()

            await self.chat_device_count_cache.connect()

            await self.sync_client()

            await self.add_device()

            await self.channel_layer.group_add(self.chat_room_name,
                                               self.channel_name)
        else:
            await self.channel_layer.group_send(
                self.personal_group, {
                    'type': 'reject_connection',
                    'reject_message': 'connection refused'
                })

        await self.channel_layer.group_discard(self.personal_group,
                                               self.channel_name)

    # Disconnect the client from the chat room and sync the chat if it's the last device
    async def disconnect(self, close_code):
        await self.remove_device()

        await self.chat_device_count_cache.disconnect()

        await self.chat_messages_cache.disconnect()

        await self.channel_layer.group_discard(self.chat_room_name,
                                               self.channel_name)
