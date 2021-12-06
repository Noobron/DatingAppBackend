from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken

from accounts.models import Photo, User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for handling `User`
    """

    age = serializers.IntegerField(source='get_age')
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    lookingFor = serializers.CharField(source='looking_for')
    dateOfBirth = serializers.DateField(source='date_of_birth')
    lastActive = serializers.DateTimeField(source='last_active')
    mainPhoto = serializers.URLField(source='main_photo')

    class Meta:
        model = User
        fields = ('username', 'introduction', 'gender', 'interests', 'city',
                  'country', 'age', 'firstName', 'lastName', 'dateOfBirth',
                  'lastActive', 'mainPhoto', 'lookingFor')


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for handling new `Photo`
    """

    id = serializers.CharField(source='public_id')

    class Meta:
        model = Photo
        fields = ('image', 'id')


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom Token Sreializer for access token
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token


class TokenRefreshSerializer(TokenRefreshSerializer):
    """
    Custom Token Sreializer for refresh token
    """

    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh_token')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise InvalidToken(
                'No valid token found in cookie \'refresh_token\'')

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username

        return token
