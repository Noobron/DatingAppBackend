from django.core import validators
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
    username = models.CharField(validators=[MinLengthValidator(3)], max_length=50, unique=True)

    # first name of the user
    first_name = models.CharField(validators=[MinLengthValidator(3)],
                                  verbose_name='first_name',
                                  max_length=75)

    # last name of the user
    last_name = models.CharField(validators=[MinLengthValidator(3)],
                                 verbose_name='last_name',
                                 max_length=75)

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