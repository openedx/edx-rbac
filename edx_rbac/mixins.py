# -*- coding: utf-8 -*-
"""
Mixin adapted from https://github.com/escodebar/django-rest-framework-rules/blob/master/rest_framework_rules/mixins.py.

Keeps py2 backward compatibility and only holds on to the necessary bits of the mixin needed.
"""
from __future__ import absolute_import, unicode_literals

import crum
from django.core.exceptions import ImproperlyConfigured
from six import string_types


class PermissionRequiredMixin:
    """
    Mixin for checking permissions with django rules.
    """

    object_permission_required = None
    permission_required = None

    def get_permission_required(self):
        """
        Return permissions required for the view it is mixed into.
        """
        if self.permission_required is None:
            # This prevents a misconfiguration of the view into which the mixin
            # is mixed. If the mixin is used, at least one permission should be
            # required.
            raise ImproperlyConfigured(
                '{0} is missing the permission_required attribute. Define '
                '{0}.permission_required, or override '
                '{0}.get_permission_required().'
                .format(self.__class__.__name__)
            )
        if isinstance(self.permission_required, string_types):
            perms = (self.permission_required, )
        else:
            perms = self.permission_required
        return perms

    def check_permissions(self, request):
        """
        Check through permissions required and throws a permission_denied if missing any.

        If `get_permission_object` is implemented, it will be called and should return the object
        for which the @rules predicate checks against.
        """
        crum.set_current_request(request)
        user = request.user

        if hasattr(self, 'get_permission_object') and callable(self.get_permission_object):
            obj = self.get_permission_object()
        else:
            obj = None

        missing_permissions = [perm for perm in self.get_permission_required()
                               if not user.has_perm(perm, obj)]

        if any(missing_permissions):
            self.permission_denied(
                request,
                message=('MISSING: {}'.format(', '.join(missing_permissions))))
