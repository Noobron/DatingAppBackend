from functools import cache
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
        self.cache = Cache("redis://" + settings.REDIS_HOST)
        self.is_user_authenticated = False
        super().__init__()

    @database_sync_to_async
    def update_last_seen(self):

        user = User.objects.filter(username=self.user_name).first()

        if user is not None and user.is_active:
            user.last_active = timezone.now()
            user.save()

    # Add current device of the User
    async def add_device(self):

        if self.cache.is_connected == False:
            await self.cache.connect()

        count = await self.cache.get(self.user_group_name)

        if count is None:
            await self.cache.set(self.user_group_name, 1)
        else:
            await self.cache.set(self.user_group_name, count + 1)

    # Remove current device of the User
    async def remove_device(self):
        if self.cache.is_connected == False:
            await self.cache.connect()

        count = await self.cache.get(self.user_group_name)

        if count is not None:
            if count <= 1:
                await self.cache.delete(self.user_group_name)
            else:
                await self.cache.set(self.user_group_name, count - 1)

    # Send the target User's status
    async def send_status(self):
        if self.cache.is_connected == False:
            await self.cache.connect()

        count = await self.cache.get(self.user_group_name)

        await self.channel_layer.group_send(
            self.user_group_name, {
                'type': 'status',
                'device_count': count if count else 0
            })

    # Try connecting the client to the target User's group
    async def connect(self):

        self.user_name = self.scope['url_route']['kwargs']['user_name'].lower()

        self.user_group_name = self.user_name + '_status'

        await self.channel_layer.group_add(self.user_group_name,
                                           self.channel_name)

        await self.accept()

        if self.scope['user'] != AnonymousUser and \
            self.scope['user'].username.lower() == self.user_name:

            self.is_user_authenticated = True
            await self.add_device()


        await self.send_status()

    async def status(self, event):
        device_count = event['device_count']

        await self.send(text_data=json.dumps(
            {'status': 'online' if device_count > 0 else 'offline'}))

    # Dsiconnect the client from the target User's group and remove device if the client is target User
    async def disconnect(self, close_code):
        if self.is_user_authenticated:
            await self.remove_device()
            await self.send_status()

        await self.cache.disconnect()

        await self.channel_layer.group_discard(self.user_group_name,
                                               self.channel_name)
