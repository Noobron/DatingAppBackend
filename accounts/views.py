from datetime import datetime
from django.http.response import HttpResponse
import json
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Photo, User

from .serializers import PhotoSerializer, UserSerializer, TokenObtainPairSerializer, TokenRefreshSerializer, RegisterSerializer

from .pagination import CustomPagination

from accounts.authentication import CustomAuthentication

from DatingAppBackend import settings


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
@authentication_classes([CustomAuthentication])
def get_users(request, name=None, *args, **kwargs):
    """
    Gets details of all or single `User`
    """

    serializer_context = {
        'request': request,
    }

    if name is None:
        user_name = ''

        if request.user.is_authenticated:
            user_name = request.user.username

        data = User.objects.filter(is_staff=False,
                                   is_active=True).exclude(username=user_name)
        paginator = CustomPagination()
        result = paginator.paginate_queryset(data, request)
        serializer = UserSerializer(result,
                                    many=True,
                                    context=serializer_context)
    else:
        data = get_object_or_404(User, username=name)
        serializer = UserSerializer(data, context=serializer_context)

    return Response(serializer.data)


@api_view(['PUT'])
def edit_profile(request, *args, **kwargs):
    """
    Edit profile details of `User`
    """

    user = get_object_or_404(User, pk=request.user.id)

    data = request.data

    print(data)

    if 'city' in data:
        user.city = data['city']

    if 'country' in data:
        user.country = data['country']

    if 'lookingFor' in data:
        user.looking_for = data['lookingFor']

    if 'interests' in data:
        user.interests = data['interests']

    if 'introduction' in data:
        user.introduction = data['introduction']

    if 'firstName' in data:
        user.first_name = data['firstName']

    if 'lastName' in data:
        user.last_name = data['lastName']

    if 'password' in data:
        user.set_password(data['password'])

    if 'mainPhoto' in data:
        user.main_photo = data['mainPhoto']

    serializer = UserSerializer(instance=user, data=data, partial=True)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([])
def get_photos(request, name, *args, **kwargs):
    """
    Gets a batch of `Photo`s of a `User`
    """
    user = get_object_or_404(User, username=name)

    if (user.is_staff
            or user.is_active == False) and request.user.is_staff == False:
        return HttpResponse('Unauthorized', status=401)

    data = Photo.objects.filter(user=user)
    paginator = CustomPagination()
    result = paginator.paginate_queryset(data, request)
    serializer = PhotoSerializer(result, many=True)

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

    if 'dateOfBirth' in request.data:
        request.data['date_of_birth'] = datetime.strptime(
            request.data['dateOfBirth'], '%Y-%m-%d').date()

    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer.save()

    return HttpResponse(json.dumps(serializer.data))


class TokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get('refresh'):
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
                                secure=True,
                                expires=datetime.today() +
                                settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])
            del response.data['refresh']
        return super().finalize_response(request, response, *args, **kwargs)
