"""
Fields to be used for djangoapps extending edx_rbac.
"""

from django import forms
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError

USER_MODEL = apps.get_model(settings.AUTH_USER_MODEL)


class UserFromEmailField(forms.EmailField):
    """
    Custom Form Field class for selecting users by entering an email.

    Meant to be used for models with foreign keys to the user table.
    """

    def clean(self, value):
        """
        Override for UserFromEmailField clean method.
        """
        try:
            user = USER_MODEL.objects.get(email=value)
        except USER_MODEL.DoesNotExist as error:
            raise ValidationError(f'User with email {value} does not exist') from error

        return user
