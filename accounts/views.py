from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAdminUser

from .models import User
from .serializers import UserSerializer, TokenObtainPairSerializer, TokenRefreshSerializer, UserDetailsSerializer


class UsersList(APIView):
    permission_classes = (IsAdminUser, )

    def get(self, request, id=None):
        """
        Action which provides response as list of all `User` or a specific `User` based on `id`
        """
        if id is None:
            data = User.objects.all()
            serializer = UserSerializer(data, many=True)
        else:
            data = get_object_or_404(User, pk=id)
            serializer = UserDetailsSerializer(data)

        return Response(serializer.data)


class TokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer


class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
