# -*- coding: utf-8 -*-
"""
Database models for edx_rbac.
"""

from __future__ import absolute_import, unicode_literals

# from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.db.models.base import ModelBase
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel
from django.db.models.fields import FieldDoesNotExist


class UserRoleAssignmentCreator(ModelBase):
    """
    The model extending UserRoleAssignment should get a foreign key to a model that is a subclass of UserRole.
    """

    def __new__(cls, name, bases, attrs):
        model = super(UserRoleAssignmentCreator, cls).__new__(cls, name, bases, attrs)
        for b in bases:
            if b.__name__ == 'UserRoleAssignment' and model.__name__ != b.__name__:
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
        return model


@python_2_unicode_compatible
class UserRole(TimeStampedModel):
    """
    Model defining a role a user can have
    """
    name = models.CharField(unique=True, max_length=255, db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        """
        Return human-readable string representation.
        """
        return self.name


@python_2_unicode_compatible
class UserRoleAssignment(TimeStampedModel):
    """
    Model for mapping users and their roles
    """
    __metaclass__ = UserRoleAssignmentCreator
    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    role_class = None

    class Meta:
        abstract = True

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
