from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from chat.models import ChatMessage

from chat.pagination import ChatMessagePagination

from chat.serializers import ChatMessageSerializer


@api_view(['GET'])
def get_chat_messages(request, chat_room_name, *args, **kwargs):
    """
    Gets unread (with additional) chat messages of a chat room
    """

    serializer_context = {
        'request': request,
    }

    data = ChatMessage.objects.filter(chat_room_name=chat_room_name)
    paginator = ChatMessagePagination()
    result = paginator.paginate_queryset(data, request)
    serializer = ChatMessageSerializer(result,
                                       many=True,
                                       context=serializer_context)

    return Response(serializer.data)


@api_view(['PUT'])
def mark_chat_message_as_seen(request,*args, **kwargs):
    """
    Marks all unread chat messages of a chat room as seen
    """

    try:

        chat_room_name = request.data['chat_room_name']

        chat_messages = ChatMessage.objects.filter(
            chat_room_name=chat_room_name, seen=False)

        for chat_message in chat_messages:
            chat_message.seen = True
            chat_message.save()

    except KeyError :
        return Response('Please try provide a chat room name',
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response('Sorry, something went wrong. Please try again later',
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)