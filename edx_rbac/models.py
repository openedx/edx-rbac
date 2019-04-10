# -*- coding: utf-8 -*-
"""
Database models for edx_rbac.
"""

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields import FieldDoesNotExist
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
from six import with_metaclass


class UserRoleAssignmentCreator(ModelBase):
    """
    The model extending UserRoleAssignment should get a foreign key to a model that is a subclass of UserRole.
    """

    def __new__(mcs, name, bases, attrs):
        """
        Override to dynamically create foreign key for objects begotten from abstract class.
        """
        model = super(UserRoleAssignmentCreator, mcs).__new__(mcs, name, bases, attrs)
        if model.__name__ != 'UserRoleAssignment' and 'UserRoleAssignment' in [b.__name__ for b in bases]:
            try:
                model._meta.get_field('role')
            except FieldDoesNotExist:
                if model.role_class and issubclass(model.role_class, UserRole):
                    model.add_to_class(
                        'role',
                        models.ForeignKey(model.role_class, db_index=True, on_delete=models.CASCADE),
                    )
                else:
                    raise Exception('role_class must be defined for any subclass of UserRole!')
        return model


@python_2_unicode_compatible
class UserRole(TimeStampedModel):
    """
    Model defining a role a user can have.
    """

    name = models.CharField(unique=True, max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        """
        Meta class for UserRole.
        """

        abstract = True

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return self.name


@python_2_unicode_compatible
class UserRoleAssignment(with_metaclass(UserRoleAssignmentCreator, TimeStampedModel)):
    """
    Model for mapping users and their roles.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE)
    role_class = None

    class Meta:
        """
        Meta class for UserRoleAssignment.
        """

        abstract = True

    def get_context(self):
        """
        Return relevant context data related to this role assignment. Defaults to returning None.
        """
        return None

    @classmethod
    def get_assignments(cls, user):
        """
        Return iterator of (rolename, context).
        """
        for assign in cls.objects.filter(
            user=user
        ).select_related('role'):
            yield assign.role.name, assign.get_context()

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return '{user}:{role}'.format(
            user=self.user.id,
            role=self.role.name,
        )

    def __repr__(self):
        """
        Return uniquely identifying string representation.
        """
        return self.__str__()
