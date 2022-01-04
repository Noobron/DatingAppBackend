from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from accounts.models import User

from chat.models import ChatMessage, ChatRoom

from chat.pagination import ChatMessagePagination

from chat.serializers import ChatMessageSerializer, ChatRoomSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_messages(request, *args, **kwargs):
    """
    Gets unread (with additional) chat messages of a chat room
    """

    other_user = request.query_params.get('other_user')
    current_user = request.user

    if other_user is None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    other_user = get_object_or_404(User, username=other_user.strip())

    chat_room_name = min(
        other_user.username, current_user.username) + '_' + max(
            other_user.username, current_user.username) + '_chat'

    chat_room = ChatRoom.objects.filter(chat_room_name=chat_room_name).first()

    serializer_context = {
        'request': request,
    }

    data = ChatMessage.objects.filter(
        chat_room=chat_room).order_by('-created_at')
    paginator = ChatMessagePagination()
    result = paginator.paginate_queryset(data, request)
    serializer = ChatMessageSerializer(result,
                                       many=True,
                                       context=serializer_context)

    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_chat_message_as_seen(request, *args, **kwargs):
    """
    Marks all unread chat messages stored in database of a chat room as seen
    """

    try:

        other_user = request.data['other_user']
        current_user = request.user

        if other_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        other_user = get_object_or_404(User, username=other_user.strip())

        chat_room_name = min(
            other_user.username, current_user.username) + '_' + max(
                other_user.username, current_user.username) + '_chat'

        chat_room = get_object_or_404(ChatRoom, chat_room_name=chat_room_name)

        chat_messages = ChatMessage.objects.filter(chat_room=chat_room,
                                                   seen=False)

        for chat_message in chat_messages:
            chat_message.seen = True
            chat_message.save()

    except KeyError:
        return Response('Please provide the other user of the chat room',
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response('Sorry, something went wrong. Please try again later',
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chat_feed(request, *args, **kwargs):
    """
    Gets the chat feed of a user
    """

    user = request.user

    if user.is_active == False:
        return Response('User is inactive', status=status.HTTP_400_BAD_REQUEST)

    serializer_context = {
        'request': request,
    }

    result = ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))
    serializer = ChatRoomSerializer(result,
                                    many=True,
                                    context=serializer_context)

    return Response(serializer.data)