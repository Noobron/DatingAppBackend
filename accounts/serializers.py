from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken

from accounts.models import Photo, User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for handling `User`
    """
    class Meta:
        model = User
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer for handling new `Photo`
    """
    class Meta:
        model = Photo
        fields = ('image', 'user')


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for handling new `User`
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {
                'write_only': True
            },
        }

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'])

        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']

        user.save()

        return user


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
