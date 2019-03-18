# -*- coding: utf-8 -*-
"""
Django admin integration for djangoapps using edx-rbac.
"""
from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from edx_rbac.admin.forms import UserRoleAssignmentAdminForm


class UserRoleAssignmentAdmin(admin.ModelAdmin):
    """
    Django admin for UserRoleAssignment.
    """

    class Meta(object):
        """
        Meta class for UserRoleAssignmentAdmin.
        """
        abstract = True

    list_display = (
        'user', 'role'
    )

    list_filter = ('role',)
    search_fields = ('user__email', 'role__name')
    fields = ('user', 'role',)
    form = UserRoleAssignmentAdminForm
