from rest_framework import serializers

from chat.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for handling `ChatMessages`
    """

    messageType = serializers.CharField(source='message_type')
    createdAt = serializers.CharField(source='created_at')
    sender = serializers.CharField(source='sender.username')
    recipient = serializers.CharField(source='recipient.username')

    class Meta:
        model = ChatMessage
        fields = ('messageType', 'sender', 'recipient', 'created_at', 'seen',
                  'content')