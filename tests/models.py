#!/usr/bin/env python
"""
These models exist solely for testing.

They are not something that gets created when you install this application.
"""

from edx_rbac.models import UserRole, UserRoleAssignment


class ConcreteUserRole(UserRole):
    """
    Used for testing the UserRole model.
    """


class ConcreteUserRoleAssignment(UserRoleAssignment):
    """
    Used for testing the UserRoleAssignment model.
    """

    role_class = ConcreteUserRole

    def get_context(self):
        """
        Generate a context string to be used in tests.
        """
        return "a-test-context"


class ConcreteUserRoleAssignmentMultipleContexts(UserRoleAssignment):
    """
    Used for testing the UserRoleAssignment model when user has multiple contexts.
    """

    role_class = ConcreteUserRole

    def get_context(self):
        """
        Generate a list with multiple contexts to be used in tests.
        """
        return ['a-test-context', 'a-second-test-context']


class ConcreteUserRoleAssignmentDuplicateContexts(UserRoleAssignment):
    """
    Used for testing the UserRoleAssignment model when user has multiple, duplicate contexts.
    """

    role_class = ConcreteUserRole

    def get_context(self):
        """
        Generate a list with multiple, duplicate contexts to be used in tests.
        """
        return ['a-test-context', 'a-second-test-context', 'a-test-context']


class ConcreteUserRoleAssignmentNoContext(UserRoleAssignment):
    """
    Used for testing the UserRoleAssignment model without context returned.
    """

    role_class = ConcreteUserRole
