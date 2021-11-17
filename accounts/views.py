from django.http.response import HttpResponse
import json
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer, TokenObtainPairSerializer, TokenRefreshSerializer, RegisterSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request, id=None, *args, **kwargs):
    """
    Gets details of all or single `User`
    """

    serializer_context = {
        'request': request,
    }

    if id is None:
        data = User.objects.all()
        serializer = UserSerializer(data,
                                    many=True,
                                    context=serializer_context)
    else:
        data = get_object_or_404(User, pk=id)
        serializer = UserSerializer(data, context=serializer_context)

    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([])
def register(request, *args, **kwargs):
    """
    Registers new `User`
    """

    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return HttpResponse(json.dumps(serializer.data))


class TokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer


class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
