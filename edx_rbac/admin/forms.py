# -*- coding: utf-8 -*-
"""
Forms to be used for djangoapps extending edx_rbac.
"""
from __future__ import absolute_import, unicode_literals

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class UserFromEmailField(forms.EmailField):
    """
    Custom Form Field class for selecting users by entering an email.
    Meant to be used for models with foreign keys to the user table.
    """

    def clean(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError('User with email {} does not exist'.format(value))

        return user


class UserRoleAssignmentAdminForm(forms.ModelForm):
    """
    Custom Form for CRUD operations on models extending UserRoleAssignment.
    """
    user = UserFromEmailField(
        label=_('User Email'),
        required=True
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        if instance:
            initial['user'] = instance.user.email
            kwargs['initial'] = initial
        super(UserRoleAssignmentAdminForm, self).__init__(*args, **kwargs)
