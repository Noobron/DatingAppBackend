import re
from caches import Cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser

from accounts.models import User

from DatingAppBackend import settings

from accounts.serializers import UserSerializer

from .tasks import update_chat_db


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer to handle real time chat between Users
    """
    def __init__(self):
        self.cache = Cache("redis://" + settings.REDIS_HOST)
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
        messages = await self.cache.get(self.chat_message_store)

        if messages is not None and len(messages) > 0:
            update_chat_db.delay(messages, self.channel_user.username,
                                 self.other_user.username)

        await self.cache.delete(self.chat_message_store)

    # Sync client with other devices if any
    async def sync_client(self):
        messages = await self.cache.get(self.chat_message_store)

        other_user_chat_feed = await self.cache.get(
            self.chat_feed_other_user_store)

        channel_user_chat_feed = await self.cache.get(
            self.chat_feed_channel_user_store)

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
            await self.cache.set(self.chat_message_store, messages)

            other_user_chat_feed = {} if other_user_chat_feed is None else other_user_chat_feed

            channel_user_chat_feed = {} if channel_user_chat_feed is None else channel_user_chat_feed

            other_user_chat_feed[
                self.channel_user.username]['lastChatMessage']['seen'] = True

            channel_user_chat_feed[
                self.other_user.username]['lastChatMessage']['seen'] = True

            await self.channel_layer.group_send(
                self.chat_feed_other_user, {
                    'type': 'update',
                    'seen': self.channel_user.username
                })

            await self.channel_layer.group_send(
                self.chat_feed_channel_user, {
                    'type': 'update',
                    'seen': self.other_user.username
                })

            await self.cache.set(self.chat_feed_other_user_store,
                                 other_user_chat_feed)

            await self.cache.set(self.chat_feed_channel_user_store,
                                 channel_user_chat_feed)

    # Add current client's device to the chat room
    async def add_device(self):

        count = await self.cache.get(self.chat_channel_user_device_count)

        if count is None:
            await self.channel_layer.group_send(
                self.chat_room_name, {
                    'type': 'availability',
                    'user_available': self.channel_user.username
                })

            await self.cache.set(self.chat_channel_user_device_count, 1)
        else:
            await self.cache.set(self.chat_channel_user_device_count,
                                 count + 1)

        other_user_chat_feed_device_count = await self.cache.get(
            self.chat_feed_other_user_device_count)

        if other_user_chat_feed_device_count is None:
            self.cache.set(self.chat_feed_other_user_device_count, 1)
        else:
            self.cache.set(self.chat_feed_other_user_device_count,
                           other_user_chat_feed_device_count + 1)

    # Remove current client's device from the chat room and sync the chat with database if no user belonging to the chat room is online
    async def remove_device(self):

        count = await self.cache.get(self.chat_channel_user_device_count)

        if count is not None:
            if count <= 1:
                await self.cache.delete(self.chat_channel_user_device_count)

                await self.channel_layer.group_send(
                    self.chat_room_name, {
                        'type': 'availability',
                        'user_not_available': self.channel_user.username
                    })

                await self.sync_chat_with_database()

            else:
                await self.cache.set(self.chat_channel_user_device_count,
                                     count - 1)

        other_user_chat_feed_device_count = await self.cache.get(
            self.chat_feed_other_user_device_count)

        if other_user_chat_feed_device_count is not None:

            if other_user_chat_feed_device_count <= 1:
                self.cache.delete(self.chat_feed_other_user_device_count)
                self.cache.delete(self.chat_feed_other_user_store)
            else:
                self.cache.set(self.chat_feed_other_user_device_count,
                               other_user_chat_feed_device_count - 1)

    # Send message to group and update message store on receiving message from client
    async def receive(self, text_data=None, bytes_data=None):

        if text_data is not None:

            data_json = json.loads(text_data)

            content = data_json['data']

            content['recipient'] = self.other_user.username

            content['sender'] = self.channel_user.username

            count = await self.cache.get(self.chat_other_user_device_count)

            if count is not None and count > 0:
                content['seen'] = True
            else:
                content['seen'] = False

            await self.channel_layer.group_send(self.chat_room_name, {
                'type': 'message',
                'content': content
            })

            messages = await self.cache.get(self.chat_message_store)

            if messages is None:
                messages = []

            messages.append(content)

            await self.cache.set(self.chat_message_store, messages)

            user1 = self.channel_user
            user2 = self.other_user

            if user1.username > user2.username:
                user1, user2 = user2, user1

            chat_room_name = user1.username + '_' + user2.username + '_chat'

            other_user_chat_feed = await self.cache.get(
                self.chat_feed_other_user_store)
            channel_user_chat_feed = await self.cache.get(
                self.chat_feed_channel_user_store)

            other_user_chat_feed = {} if other_user_chat_feed is None else other_user_chat_feed

            channel_user_chat_feed = {} if channel_user_chat_feed is None else channel_user_chat_feed

            if self.channel_user.username in other_user_chat_feed:
                other_user_chat_feed[
                    self.channel_user.username]['lastChatMessage'] = content

                channel_user_chat_feed[
                    self.other_user.username]['lastChatMessage'] = content

            else:
                other_user_chat_feed[self.channel_user.username] = {
                    'chatRoomName': chat_room_name,
                    'lastChatMessage': content,
                    'firstUser': UserSerializer(instance=user1).data,
                    'secondUser': UserSerializer(instance=user2).data
                }

                channel_user_chat_feed[self.other_user.username] = {
                    'chatRoomName': chat_room_name,
                    'lastChatMessage': content,
                    'firstUser': UserSerializer(instance=user1).data,
                    'secondUser': UserSerializer(instance=user2).data
                }

            await self.channel_layer.group_send(
                self.chat_feed_other_user, {
                    'type': 'feed',
                    'chat_room':
                    other_user_chat_feed[self.channel_user.username],
                    'other_user': self.channel_user.username
                })

            await self.channel_layer.group_send(
                self.chat_feed_channel_user, {
                    'type': 'feed',
                    'chat_room':
                    channel_user_chat_feed[self.other_user.username],
                    'other_user': self.other_user.username
                })

            await self.cache.set(self.chat_feed_other_user_store,
                                 other_user_chat_feed)

            await self.cache.set(self.chat_feed_channel_user_store,
                                 channel_user_chat_feed)

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

    async def availability(self, event):

        if 'user_not_available' in event:
            user = event['user_not_available']

            await self.send(text_data=json.dumps({
                'type': 'availability',
                'user_not_available': user
            }))

        if 'user_available' in event:
            user = event['user_available']

            await self.send(text_data=json.dumps({
                'type': 'availability',
                'user_available': user
            }))

    async def feed(self, event):
        chat_room = event['chat_room']

        other_user = event['other_user']

        await self.send(text_data=json.dumps({
            'type': 'feed',
            'chat_room': chat_room,
            'other_user': other_user
        }))

    async def update(self, event):
        seen = event['seen']

        await self.send(text_data=json.dumps({'type': 'update', 'seen': seen}))

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

            self.chat_channel_user_device_count = self.chat_room_name + '_' + self.channel_user.username + '_device_count'

            self.chat_other_user_device_count = self.chat_room_name + '_' + self.other_user.username + '_device_count'

            self.chat_message_store = self.chat_room_name + '_message_store'

            self.chat_feed_other_user = self.other_user.username + '_chat_feed'

            self.chat_feed_other_user_store = self.other_user.username + '_chat_feed_store'

            self.chat_feed_other_user_device_count = self.other_user.username + '_chat_feed_device_count'

            self.chat_feed_channel_user = self.channel_user.username + '_chat_feed'

            self.chat_feed_channel_user_store = self.channel_user.username + '_chat_feed_store'

            await self.cache.connect()

            await self.sync_client()

            await self.channel_layer.group_add(self.chat_room_name,
                                               self.channel_name)

            await self.channel_layer.group_add(self.chat_feed_other_user,
                                               self.channel_name)

            await self.channel_layer.group_add(self.chat_feed_channel_user,
                                               self.channel_name)

            await self.add_device()
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

        await self.cache.disconnect()

        await self.channel_layer.group_discard(self.chat_room_name,
                                               self.channel_name)


class ChatFeedConsumer(AsyncWebsocketConsumer):
    """
    Consumer to handle chat feeds
    """
    def __init__(self):
        self.cache = Cache("redis://" + settings.REDIS_HOST)
        super().__init__()

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

    async def sync_client(self):
        feeds = await self.cache.get(self.chat_feed_channel_user_store)

        if feeds is not None:
            for feed in feeds:
                await self.channel_layer.group_send(self.personal_group, {
                    'type': 'feed',
                    'chat_room': feeds[feed],
                    'other_user': feed
                })

    async def feed(self, event):
        chat_room = event['chat_room']

        other_user = event['other_user']

        await self.send(text_data=json.dumps({
            'type': 'feed',
            'chat_room': chat_room,
            'other_user': other_user
        }))

    async def update(self, event):
        seen = event['seen']

        await self.send(text_data=json.dumps({'type': 'update', 'seen': seen}))

    async def connect(self):

        # Group specific for the channel to send synced messages or connection result back to the client
        self.personal_group = re.sub(r'[^0-9a-zA-Z]+', '-',
                                     self.channel_name) + "_personal_group"

        await self.channel_layer.group_add(self.personal_group,
                                           self.channel_name)

        await self.accept()

        if self.scope['user'] == AnonymousUser:
            await self.channel_layer.group_send(
                self.personal_group, {
                    'type': 'reject_connection',
                    'reject_message': 'connection refused'
                })
            return

        await self.channel_layer.group_send(
            self.personal_group, {
                'type': 'accept_connection',
                'accept_message': 'connection accepted'
            })

        self.channel_user = self.scope['user']

        self.chat_feed_channel_user_store = self.channel_user.username + '_chat_feed_store'

        self.chat_feed_channel_user = self.channel_user.username + '_chat_feed'

        await self.cache.connect()

        await self.sync_client()

        await self.channel_layer.group_add(self.chat_feed_channel_user,
                                           self.channel_name)

    async def disconnect(self, code):

        await self.cache.disconnect()

        await self.channel_layer.group_discard(self.personal_group,
                                               self.channel_name)

        await self.channel_layer.group_discard(self.chat_feed_channel_user,
                                               self.channel_name)
