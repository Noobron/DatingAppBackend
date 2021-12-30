from rest_framework import serializers

from accounts.serializers import UserSerializer

from chat.models import ChatMessage, ChatRoom


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for handling `ChatMessage`
    """

    messageType = serializers.CharField(source='message_type')
    createdAt = serializers.CharField(source='created_at')
    sender = serializers.CharField(source='sender.username')
    recipient = serializers.CharField(source='recipient.username')

    class Meta:
        model = ChatMessage
        fields = ('messageType', 'sender', 'recipient', 'createdAt', 'seen',
                  'content')


class ChatRoomSerializer(serializers.ModelSerializer):
    """
    Serializer for handling `ChatRoom`
    """

    chatRoomName = serializers.CharField(source='chat_room_name')
    lastChatMessage = ChatMessageSerializer(source='last_chat_message')
    firstUser = UserSerializer(source='user1')
    secondUser = UserSerializer(source='user2')

    class Meta:
        model = ChatRoom
        fields = ('chatRoomName', 'lastChatMessage', 'firstUser', 'secondUser')
