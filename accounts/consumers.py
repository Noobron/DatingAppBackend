from caches import Cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from accounts.models import User

from DatingAppBackend import settings


class StatusConsumer(AsyncWebsocketConsumer):
    """
    Consumer to handle online status of authenticated Users
    """
    def __init__(self):
        self.device_count_cache = Cache("redis://" + settings.REDIS_HOST)
        self.is_user_authenticated = False
        super().__init__()

    # Get the valid User from database
    @database_sync_to_async
    def get_user(self, username):
        user = User.objects.filter(username=username).first()

        if user is not None and user.is_active:
            return user
        else:
            return AnonymousUser

    @database_sync_to_async
    def update_last_active(self, last_active_time):

        user = User.objects.filter(username=self.user_name).first()

        if user is not None and user.is_active:
            user.last_active = last_active_time
            user.save()

    # Add current device of the User
    async def add_device(self):

        count = await self.device_count_cache.get(self.user_device_count)

        if count is None:
            await self.device_count_cache.set(self.user_device_count, 1)
            count = 1
        else:
            await self.device_count_cache.set(self.user_device_count,
                                              count + 1)
            count += 1

        await self.send_status(count)

    # Remove current device of the User
    async def remove_device(self):

        count = await self.device_count_cache.get(self.user_device_count)

        if count is not None:
            if count <= 1:
                await self.device_count_cache.delete(self.user_device_count)
                count = None
                last_active_time = timezone.now()
                await self.update_last_active(last_active_time)
                self.last_active_time = last_active_time.isoformat()
                await self.send_status(count)
            else:
                await self.device_count_cache.set(self.user_device_count,
                                                  count - 1)
                count -= 1

    # Send the target User's status
    async def send_status(self, count):

        if count is not None and count > 0:
            await self.channel_layer.group_send(self.user_group_name, {
                'type': 'status',
                'device_count': count
            })
        else:
            await self.channel_layer.group_send(
                self.user_group_name, {
                    'type': 'time',
                    'last_active': self.last_active_time
                })

    # Try connecting the client to the target User's group
    async def connect(self):

        self.user_name = self.scope['url_route']['kwargs']['user_name']

        target_user = await self.get_user(self.user_name)

        if target_user == AnonymousUser:
            return

        self.user_name = target_user.username

        self.last_active_time = target_user.last_active.isoformat()

        self.user_group_name = self.user_name + '_status'

        self.user_device_count = self.user_name + '_device_count'

        await self.channel_layer.group_add(self.user_group_name,
                                           self.channel_name)

        await self.accept()

        await self.device_count_cache.connect()

        if self.scope['user'] != AnonymousUser and \
            self.scope['user'].username == self.user_name:
            self.is_user_authenticated = True
            await self.add_device()
        else:
            count = await self.device_count_cache.get(self.user_device_count)
            await self.send_status(count)

    async def status(self, event):
        device_count = event['device_count']

        await self.send(text_data=json.dumps(
            {
                'type': 'status',
                'status': 'online' if device_count > 0 else None
            }))

    async def time(self, event):
        last_active = event['last_active']

        await self.send(text_data=json.dumps({
            'type': 'time',
            'last_active': last_active
        }))

    # Disconnect the client from the target User's group and remove device if the client is target User
    async def disconnect(self, close_code):
        if self.is_user_authenticated:
            await self.remove_device()

        await self.device_count_cache.disconnect()

        await self.channel_layer.group_discard(self.user_group_name,
                                               self.channel_name)
