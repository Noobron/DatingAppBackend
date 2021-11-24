from datetime import datetime
from django.http.response import HttpResponse
import json
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated

from .models import Photo, User
from .serializers import PhotoSerializer, UserSerializer, TokenObtainPairSerializer, TokenRefreshSerializer, RegisterSerializer


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


@api_view(['PUT'])
def edit_profile(request, *args, **kwargs):
    """
    Edit profile details of `User`
    """

    user = get_object_or_404(User, pk=request.user.id)

    data = request.data

    if 'city' in data:
        user.city = data['city']

    if 'country' in data:
        user.country = data['country']

    if 'gender' in data:
        user.gender = data['gender']

    if 'looking_for' in data:
        user.looking_for = data['looking_for']

    if 'interests' in data:
        user.interests = data['interests']

    if 'introduction' in data:
        user.introduction = data['introduction']

    if 'first_name' in data:
        user.first_name = data['first_name']

    if 'last_name' in data:
        user.last_name = data['last_name']

    if 'date_of_birth' in data:
        user.date_of_birth = datetime.strptime(data['date_of_birth'],
                                               '%Y-%m-%d').date()

    if 'password' in data:
        user.set_password(data['password'])

    if 'main_photo' in data:
        user.main_photo = data['main_photo']

    serializer = UserSerializer(instance=user, data=data, partial=True)

    if serializer.is_valid(raise_exception=True):
        #serializer.save()
        pass

    return Response(serializer.data)


@api_view(['POST'])
def add_photo(request, *args, **kwargs):
    """
    Add a new `Photo` for current `User`
    """

    request.data['user'] = request.user.id

    photo = Photo(image=request.data['image'], user=request.user)

    serializer = PhotoSerializer(instance=photo, data=request.data)

    if (serializer.is_valid(raise_exception=True)):
        photo.save()

    return HttpResponse(json.dumps({'message': "Uploaded"}), status=200)


@authentication_classes([])
def deleteJWTToken(request):
    """
    Delete JWT Token when `User` logs out
    """
    response = HttpResponse()
    response.delete_cookie("refresh_token", path="/")
    return response


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

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            response.set_cookie('refresh_token',
                                response.data['refresh'],
                                httponly=True,
                                samesite='Lax',
                                secure=True)
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)


class TokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
            response.set_cookie('refresh_token',
                                response.data['refresh'],
                                httponly=True,
                                samesite='Lax',
                                secure=True)
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)
