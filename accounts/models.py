from datetime import datetime, date
from django.core.validators import MinLengthValidator
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)


class UserManager(BaseUserManager):
    """
    Mananger class for `User` objects.
    """
    def create_user(self, username, password):
        """
        Create and return a `User` with a username and password.
        """
        if username is None:
            raise TypeError('User must have a username.')

        if password is None:
            raise TypeError('User must have a password.')

        user = self.model(username=username)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, password)
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser):
    """
    Custom `User` Model for handling accounts in the backend
    """

    # unique user name of the user
    username = models.CharField(validators=[MinLengthValidator(3)],
                                max_length=50,
                                unique=True)

    # first name of the user
    first_name = models.CharField(validators=[MinLengthValidator(3)],
                                  verbose_name='first_name',
                                  max_length=75)

    # last name of the user
    last_name = models.CharField(validators=[MinLengthValidator(3)],
                                 verbose_name='last_name',
                                 max_length=75)

    # date of birth of the user
    date_of_birth = models.DateField(null=True)

    # day on which user created the account
    date_of_creation = models.DateField(default=datetime.today)

    # last time user was active
    last_active = models.DateTimeField(default=datetime.now)

    # preferred gender of the user
    gender = models.CharField(max_length=25, default='Not Disclosed')

    # introduction of the  user
    introduction = models.TextField(null=True)

    # looking for preference
    looking_for = models.TextField(null=True)

    # interests of the user
    interests = models.CharField(max_length=100, null=True)

    # city of the user
    city = models.CharField(max_length=40, null=True)

    # country of the user
    country = models.CharField(max_length=40, null=True)

    # main photo (URL) of the user
    main_photo = models.URLField(
        max_length=250,
        default=
        'https://static-media-prod-cdn.itsre-sumo.mozilla.net/static/sumo/img/default-FFA-avatar.png'
    )

    # field to get user activation status
    is_active = models.BooleanField(default=True)

    # whether current user is having staff permissions
    is_staff = models.BooleanField(default=False)

    # The `USERNAME_FIELD` property sets username field to be required for logging in.
    USERNAME_FIELD = 'username'

    # instance of `UseManager` will manage objects of `User` type
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User` by providing username.
        """
        return self.username

    def get_age(self):
        """
        Gets the age of `User`
        """

        age = -1

        if self.date_of_birth: 
            today = date.today()
            age = today.year - self.date_of_birth.year - (
                (today.month, today.day) <
                (self.date_of_birth.month, self.date_of_birth.day))

        return age


def user_photos_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<user_id>/photos/<filename>
    return '{0}/photos/{1}'.format(instance.user.id, filename)


class Photo(models.Model):
    """
    Class for sotring images uploaded by user in their profile
    """

    # user field
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # image uploaded by user
    image = models.ImageField(upload_to=user_photos_path)
