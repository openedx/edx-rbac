# -*- coding: utf-8 -*-
"""
Tests for the `edx-rbac` utilities module.
"""
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from mock import patch

from edx_rbac.utils import (
    ALL_ACCESS_CONTEXT,
    create_role_auth_claim_for_user,
    request_user_has_implicit_access_via_jwt,
    user_has_access_via_database
)
from tests.models import (
    ConcreteUserRole,
    ConcreteUserRoleAssignment,
    ConcreteUserRoleAssignmentMultipleContexts,
    ConcreteUserRoleAssignmentNoContext
)


class TestUtils(TestCase):
    """
    TestUtils tests.
    """

    def setUp(self):
        super(TestUtils, self).setUp()
        self.request = RequestFactory().get('/')
        self.user = User.objects.create(username='test_user', password='pw')
        self.request.user = self.user

    # Check out test_settings for the variable declaration
    def test_request_user_has_implicit_access_via_jwt(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about
        """
        toy_decoded_jwt = {
          "roles": [
            "coupon-manager:some_context"
          ]
        }
        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
        )

    def test_request_user_has_implicit_access_via_jwt_no_context(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about
        """
        toy_decoded_jwt = {
          "roles": [
            "coupon-manager"
          ]
        }
        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
        )

    def test_request_user_has_no_implicit_access_via_jwt(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about
        """
        toy_decoded_jwt = {
          "roles": [
            "coupon-manager:some_context"
          ]
        }
        assert not request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'superuser-access',
        )

    def test_request_user_has_no_implicit_access_when_jwt_absent(self):
        """
        Helper function should return False when JWT is absent
        """
        toy_decoded_jwt = None
        assert not request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'superuser-access',
        )

    def test_request_user_has_implicit_access_via_jwt_with_context(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about. This case handles checking if the context matches.
        """
        toy_decoded_jwt = {
            "roles": [
                "coupon-manager:some_context"
            ]
        }
        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'some_context'
        )

    def test_request_user_has_implicit_access_via_jwt_with_all_acess_context(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if user role matches with a system wide
        role and context matches with `ALL_ACCESS_CONTEXT`.
        """
        toy_decoded_jwt = {
            'roles': [
                'enterprise_openedx_operator:*'
            ]
        }
        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'enterprise_data_admin',
            'some_context'
        )

    def test_request_user_has_no_implicit_access_via_jwt_with_context(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about. This case handles checking if the context matches.
        """
        toy_decoded_jwt = {
            "roles": [
                "coupon-manager:some_context"
            ]
        }
        assert not request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'not_the_right_context'
        )

    def test_request_user_has_no_implicit_access_via_jwt_no_context(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about. This case handles checking if the context matches.
        """
        toy_decoded_jwt = {
            "roles": [
                "coupon-manager"
            ]
        }
        assert not request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'some_context'
        )

    def test_user_with_multiple_contexts_has_access_via_jwt(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about. This case handles checking if each available context
        matches when the user has access to multiple contexts.
        """
        toy_decoded_jwt = {
            "roles": [
                "coupon-manager:some_context",
                "coupon-manager:some_other_context"
            ]
        }
        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'some_context'
        )

        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'some_other_context'
        )

    def test_user_multiple_contexts_has_access_via_jwt_with_all_access_context(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about. This case handles checking if a context not specified
        in the jwt matches when the user has access to multiple contexts,
        one of which is the all access context.
        """
        toy_decoded_jwt = {
            "roles": [
                "coupon-manager:some_context",
                "coupon-manager:*"
            ]
        }

        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'some_context'
        )

        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'some_totally_different_context'
        )

    def test_user_with_multiple_contexts_has_no_access_via_jwt(self):
        """
        Helper function should discern what roles user has based on role data
        in jwt, and then return true if any of those match the role we're
        asking about. This case handles checking if a non-available context
        does not match when the user has access to multiple other contexts.
        """
        toy_decoded_jwt = {
            "roles": [
                "coupon-manager:some_context",
                "coupon-manager:some_other_context"
            ]
        }
        assert not request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            'coupon-management',
            'some_totally_different_context'
        )


class TestUtilsWithDatabaseRequirements(TestCase):
    """
    TestUtilsWithDatabaseRequirements tests.
    """

    def setUp(self):
        super(TestUtilsWithDatabaseRequirements, self).setUp()
        self.user = User.objects.get_or_create(username='test_user', password='pw')[0]
        self.role = ConcreteUserRole.objects.get_or_create(name='coupon-manager')[0]

    def test_user_has_access_via_database(self):
        """
        Access check should return true if RoleAssignment exists for user
        """
        ConcreteUserRoleAssignment.objects.create(
            user=self.user,
            role=self.role
        )
        assert user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignment,
        )

    def test_user_has_no_access_via_database(self):
        """
        Access check should return false if RoleAssignment does not exist for user
        """
        assert not user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignment,
        )

    def test_user_has_access_via_database_with_context(self):
        """
        Access check should return true if RoleAssignment exists for user.
        This case handles checking if the context matches.
        """
        ConcreteUserRoleAssignment.objects.create(
            user=self.user,
            role=self.role
        )
        assert user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignment,
            'a-test-context'
        )

    def test_user_with_multiple_contexts_has_access_via_database(self):
        """
        Access check should return true if RoleAssignment exists for user with multiple contexts.
        """
        ConcreteUserRoleAssignmentMultipleContexts.objects.create(
            user=self.user,
            role=self.role
        )
        assert user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignmentMultipleContexts,
            'a-test-context'
        )
        assert user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignmentMultipleContexts,
            'a-second-test-context'
        )

    def test_user_has_access_via_database_with_all_access_context(self):
        """
        Access check should return true if RoleAssignment exists for user.
        This case handles checking if the role assignment has `ALL_ACCESS_CONTEXT` context.
        """
        ConcreteUserRoleAssignment.objects.create(
            user=self.user,
            role=self.role
        )

        with patch('tests.models.ConcreteUserRoleAssignment.get_context', return_value=ALL_ACCESS_CONTEXT):
            assert user_has_access_via_database(
                self.user,
                'coupon-manager',
                ConcreteUserRoleAssignment,
                'some_context'
            )

    def test_user_with_multiple_contexts_has_access_via_database_with_all_access_context(self):
        """
        Access check should return true if the correct RoleAssignment exists for user.
        This case handles checking if the role assignment has `ALL_ACCESS_CONTEXT` as part of multiple contexts.
        """
        ConcreteUserRoleAssignmentMultipleContexts.objects.create(
            user=self.user,
            role=self.role
        )

        with patch(
                'tests.models.ConcreteUserRoleAssignmentMultipleContexts.get_context',
                return_value=[u'some_context', ALL_ACCESS_CONTEXT]
        ):
            assert user_has_access_via_database(
                self.user,
                'coupon-manager',
                ConcreteUserRoleAssignmentMultipleContexts,
                'a_context_bypassed_by_all_access_context'
            )

    def test_user_has_no_access_via_database_with_context(self):
        """
        Access check should return false if the right RoleAssignment context does not exist for user.
        """
        ConcreteUserRoleAssignment.objects.create(
            user=self.user,
            role=self.role
        )

        assert not user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignment,
            'not_the_right_context'
        )

    def test_user_with_multiple_contexts_has_no_access_via_database(self):
        """
        Access check should return false if the right RoleAssignment context does not exist for user with multiple
        contexts.
        """
        ConcreteUserRoleAssignmentMultipleContexts.objects.create(
            user=self.user,
            role=self.role
        )

        assert not user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignmentMultipleContexts,
            'not_the_right_context'
        )

    def test_user_has_no_access_via_database_no_context(self):
        """
        Access check should return false if RoleAssignment does not exist for user.
        This case handles checking if the context matches.
        """
        ConcreteUserRoleAssignmentNoContext.objects.create(
            user=self.user,
            role=self.role
        )

        assert not user_has_access_via_database(
            self.user,
            'coupon-manager',
            ConcreteUserRoleAssignment,
            'not_the_right_context'
        )

    def test_create_role_auth_claim_for_user(self):
        """
        Helper function should create a list of strings based on the roles
        associated with the user.
        """
        ConcreteUserRoleAssignment.objects.create(
            user=self.user,
            role=self.role
        )

        expected_claim = [
            'coupon-manager:a-test-context',
            'test-role',
            'test-role2:1',
        ]
        actual_claim = create_role_auth_claim_for_user(self.user)
        assert expected_claim == actual_claim

    def test_create_role_auth_claim_for_user_with_multiple_contexts(self):
        """
        Helper function should create a list of strings based on the roles
        associated with the user with multiple contexts.
        """
        ConcreteUserRoleAssignmentMultipleContexts.objects.create(
            user=self.user,
            role=self.role
        )

        expected_claim = [
            'coupon-manager:a-test-context',
            'coupon-manager:a-second-test-context',
            'test-role',
            'test-role2:1',
        ]
        actual_claim = create_role_auth_claim_for_user(self.user)
        assert expected_claim == actual_claim
