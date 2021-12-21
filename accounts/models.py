from datetime import datetime, date
from django.core.validators import MinLengthValidator
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.contrib.postgres.fields import CICharField

from DatingAppBackend import settings

def calculate_age(born):
    """
    Calculates age
    """
    today = date.today()
    return today.year - born.year - ((today.month, today.day) <
                                     (born.month, born.day))


@deconstructible
class MinAgeValidator(object):
    def __init__(self, minimum_age):
        self.minimum_age = minimum_age

    def __call__(self, value):
        if calculate_age(value) < self.minimum_age:
            raise ValidationError(str(calculate_age(value)) +
                                  ' is less than minimum age: ' +
                                  str(self.minimum_age),
                                  params={'value': value})


class UserManager(BaseUserManager):
    """
    Mananger class for `User` objects.
    """
    def create_user(self,
                    username,
                    password,
                    gender,
                    date_of_birth,
                    first_name='',
                    last_name='',
                    check_for_validation=False):
        """
        Create and return a `User` with a username and password.
        """
        if username is None:
            raise TypeError('User must have a username.')

        if password is None:
            raise TypeError('User must have a password.')

        if gender is None:
            raise TypeError('User must have a gender')

        if date_of_birth is None:
            raise TypeError('User must have a date of birth')

        user = self.model(username=username.strip(),
                          date_of_birth=date_of_birth,
                          gender=gender.strip().lower(),
                          first_name=first_name.strip(),
                          last_name=last_name.strip())
        user.set_password(password.strip())

        if check_for_validation == True:
            user.full_clean()

        user.save()

        return user

    def create_superuser(self,
                         username,
                         password,
                         gender,
                         date_of_birth,
                         first_name='',
                         last_name='',
                         check_for_validation=False):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, password, gender, date_of_birth,
                                first_name, last_name, check_for_validation)
        user.is_staff = True

        if check_for_validation == True:
            user.full_clean()

        user.save()

        return user


class User(AbstractBaseUser):
    """
    Custom `User` Model for handling accounts in the backend
    """

    # unique user name of the user
    username = CICharField(validators=[MinLengthValidator(3)],
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
    date_of_birth = models.DateField(validators=[MinAgeValidator(18)])

    # day on which user created the account
    date_of_creation = models.DateField(default=datetime.today)

    # last time user was active
    last_active = models.DateTimeField(default=timezone.now)

    # preferred gender of the user
    gender = models.CharField(max_length=25)

    # introduction of the  user
    introduction = models.TextField(null=True, blank=True)

    # looking for preference
    looking_for = models.TextField(null=True, blank=True)

    # interests of the user
    interests = models.CharField(max_length=100, null=True, blank=True)

    # city of the user
    city = models.CharField(max_length=40, null=True, blank=True)

    # country of the user
    country = models.CharField(max_length=40, null=True, blank=True)

    # main photo (URL) of the user
    main_photo = models.URLField(
        default=
        settings.DEFAULT_PROFILE_URL,
        max_length=1000)

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

        return calculate_age(self.date_of_birth)


def user_photos_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/<user_id>/photos/<filename>
    return '{0}/photos/{1}'.format(instance.user.id, filename)


class Photo(models.Model):
    """
    Class for storing image urls uploaded by user in their profile
    """

    # user field
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # URL for image uploaded by user
    image = models.URLField(max_length=1000)

    # public ID of the image associated with Cloudinary
    public_id = models.CharField(max_length=100, unique=True)
