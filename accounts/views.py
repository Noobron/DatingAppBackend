from datetime import datetime
from django.http.response import HttpResponse
import requests
import imghdr
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Photo, User

from .serializers import PhotoSerializer, UserSerializer, TokenObtainPairSerializer, TokenRefreshSerializer

from .pagination import CustomPagination

from accounts.authentication import CustomAuthentication

from DatingAppBackend import settings

import cloudinary.uploader


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


@api_view(['GET'])
@authentication_classes([])
def get_photos(request, name, *args, **kwargs):
    """
    Gets a batch of `Photo`s of a `User`
    """
    user = get_object_or_404(User, username=name)

    if (user.is_staff
            or user.is_active == False) and request.user.is_staff == False:
        return Response('Unauthorized', status=401)

    data = Photo.objects.filter(user=user)
    paginator = CustomPagination()
    result = paginator.paginate_queryset(data, request)
    serializer = PhotoSerializer(result, many=True)

    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([])
def register(request, *args, **kwargs):
    """
    Registers new `User`
    """

    try:

        if 'dateOfBirth' in request.data:
            date = datetime.strptime(str(request.data['dateOfBirth']),
                                     '%Y-%m-%d').date()

        # check for validation

        user = User.objects.create_user(
            username=str(request.data['username']),
            password=str(request.data['password']),
            first_name=str(request.data['firstName']),
            last_name=str(request.data['lastName']),
            gender=str(request.data['gender']),
            date_of_birth=date,
            check_for_validation=True)
    except ValidationError as e:
        return Response(e, status=400)
    except ValueError as e:
        return Response("Please enter dateOfBirth field", status=400)
    except Exception as e:
        return Response(
            'Server encountered an issue while processing the request',
            status=500)

    serializer = UserSerializer(instance=user)

    return Response(serializer.data)


@api_view(['POST'])
def add_photo(request, *args, **kwargs):
    """
    Add a new `Photo` for current `User`
    """

    image_file = request.data['image']

    try:

        if imghdr.what(image_file) is None:
            raise Exception('Please upload a valid image file')

        cloudinary_upload_response = cloudinary.uploader.upload(
            image_file, folder="files/" + str(request.user.id) + "/photos")

        photo = Photo(image=cloudinary_upload_response['secure_url'],
                      public_id=cloudinary_upload_response['public_id'],
                      user=request.user)

        # check for validation
        photo.full_clean()

        photo.save()

    except FileNotFoundError:
        return Response("'image' field should not be empty", status=400)
    except Exception as e:
        return Response('Sorry, something went wrong. Please try again later',
                        status=400)

    return Response({
        'image': cloudinary_upload_response['secure_url'],
        'id': cloudinary_upload_response['public_id']
    })


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    if r.status_code == 200 and r.headers["content-type"] in image_formats:
        return True
    return False


@api_view(['PUT'])
def edit_profile(request, *args, **kwargs):
    """
    Edit profile details of `User`
    """

    user = get_object_or_404(User, pk=request.user.id)

    data = request.data

    try:

        if 'city' in data:
            user.city = data['city'].strip()

        if 'country' in data:
            user.country = data['country'].strip()

        if 'lookingFor' in data:
            user.looking_for = data['lookingFor'].strip()

        if 'interests' in data:
            user.interests = data['interests'].strip()

        if 'introduction' in data:
            user.introduction = data['introduction'].strip()

        if 'firstName' in data:
            user.first_name = data['firstName'].strip()

        if 'lastName' in data:
            user.last_name = data['lastName'].strip()

        if 'password' in data:
            user.set_password(data['password']).strip()

        if 'mainPhoto' in data:
            img = data['mainPhoto'].strip()
            if img == '':
                img = settings.DEFAULT_PROFILE_URL
            elif is_url_image(img) is False:
                return Response('Please send a valid URL for profile photo',
                                status=400)

            user.main_photo = img

        # check for validation

        user.full_clean()

        user.save()

    except ValidationError as e:
        return Response(e, status=400)
    except Exception as e:
        return Response('Sorry, something went wrong. Please try again later',
                        status=500)

    serializer = UserSerializer(instance=user)

    return Response(serializer.data)


@api_view(['DELETE'])
def delete_photo(request, *args, **kwargs):
    """
    Delete `Photo` for current `User`
    """

    if 'id' not in request.data:
        return Response('id of the image not provided', status=400)

    photo = get_object_or_404(Photo,
                              user=request.user,
                              public_id=request.data['id'])

    response = cloudinary.uploader.destroy(public_id=request.data['id'])

    if response['result'] == 'ok':
        photo.delete()
    else:
        return Response('Sorry, something went wrong. Please try again later',
                        status=400)

    return Response(status=204)


@authentication_classes([])
def deleteJWTToken(request):
    """
    Delete JWT Token when `User` logs out
    """
    response = HttpResponse()
    response.delete_cookie("refresh_token", path="/")
    return response


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
