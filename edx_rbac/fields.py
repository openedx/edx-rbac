# -*- coding: utf-8 -*-
"""
Fields to be used for djangoapps extending edx_rbac.
"""
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError('User with email {} does not exist'.format(value))

        return user
