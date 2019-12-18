#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
These models exist solely for testing.

They are not something that gets created when you install this application.
"""

from __future__ import absolute_import, unicode_literals

from edx_rbac.models import UserRole, UserRoleAssignment


class ConcreteUserRole(UserRole):  # pylint: disable=model-no-explicit-unicode
    """
    Used for testing the UserRole model.
    """

    pass


class ConcreteUserRoleAssignment(UserRoleAssignment):  # pylint: disable=model-no-explicit-unicode
    """
    Used for testing the UserRoleAssignment model.
    """

    role_class = ConcreteUserRole

    def get_context(self):
        """
        Generate a context string to be used in tests.
        """
        return "a-test-context"


class ConcreteUserRoleAssignmentMultipleContexts(UserRoleAssignment):  # pylint: disable=model-no-explicit-unicode
    """
    Used for testing the UserRoleAssignment model when user has multiple contexts.
    """

    role_class = ConcreteUserRole

    def get_context(self):
        """
        Generate a list with multiple contexts to be used in tests.
        """
        return [u'a-test-context', u'a-second-test-context']


class ConcreteUserRoleAssignmentNoContext(UserRoleAssignment):  # pylint: disable=model-no-explicit-unicode
    """
    Used for testing the UserRoleAssignment model without context returned.
    """

    role_class = ConcreteUserRole
