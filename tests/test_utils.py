# -*- coding: utf-8 -*-
"""
Tests for the `edx-rbac` utilities module.
"""
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from edx_rest_framework_extensions.auth.jwt.cookies import jwt_cookie_name
# edx_rest_framework_extensions test utils should change when the package
# does. Given edx_rbac is tightly coupled to edx_rest_framework_extensions,
# using those utils seems reasonable in the way of not repeating ourselves
from edx_rest_framework_extensions.auth.jwt.tests.utils import generate_jwt_token, generate_unversioned_payload
from mock import patch

from edx_rbac.utils import (
    create_role_auth_claim_for_user,
    get_decoded_jwt_from_request,
    get_request_or_stub,
    request_user_has_implicit_access_via_jwt,
    user_has_access_via_database
)
from tests.models import ConcreteUserRole, ConcreteUserRoleAssignment, ConcreteUserRoleAssignmentNoContext


class TestUtils(TestCase):
    """
    TestUtils tests.
    """

    def setUp(self):
        super(TestUtils, self).setUp()
        self.request = RequestFactory().get('/')
        self.user = User.objects.create(username='test_user', password='pw')
        self.request.user = self.user

    def test_get_request_or_stub(self):
        """
        Outside the context of the request, we should still get a request
        that allows us to build an absolute URI.
        """
        stub = get_request_or_stub()
        expected_url = "http://{site_name}/foobar".format(site_name=settings.SITE_NAME)
        self.assertEqual(stub.build_absolute_uri("foobar"), expected_url)

    @patch('edx_rbac.utils.jwt_decode_handler')
    def test_get_decoded_jwt_from_request(self, mock_decoder):
        """
        A decoded jwt should be returned from request if it exists
        """
        payload = generate_unversioned_payload(self.request.user)
        payload.update({
          "roles": [
            "some_new_role_name:some_context"
          ]
        })
        jwt_token = generate_jwt_token(payload)

        self.request.COOKIES[jwt_cookie_name()] = jwt_token
        get_decoded_jwt_from_request(self.request)

        mock_decoder.assert_called_once()

    @patch('edx_rbac.utils.jwt_decode_handler')
    def test_get_decoded_jwt_from_request_no_jwt_in_request(self, mock_decoder):
        """
        None should be returned if the request has no jwt
        """
        result = get_decoded_jwt_from_request(self.request)

        assert result is None
        mock_decoder.assert_not_called()

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


class TestUtilsWithDatabaseRequirements(TestCase):
    """
    TestUtilsWithDatabaseRequirements tests.
    """

    def setUp(self):
        super(TestUtilsWithDatabaseRequirements, self).setUp()
        self.user = User.objects.create(username='test_user', password='pw')
        self.role = ConcreteUserRole(name='coupon-manager')
        self.role.save()

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

    def test_user_has_access_via_database_with_no_context(self):
        """
        Access check should return true if RoleAssignment exists for user.
        This case handles checking if the context matches.
        """
        ConcreteUserRoleAssignment.objects.create(
            user=self.user,
            role=self.role
        )

        with patch('tests.models.ConcreteUserRoleAssignment.get_context', return_value=None) as mock_get_context:
            assert user_has_access_via_database(
                self.user,
                'coupon-manager',
                ConcreteUserRoleAssignment,
                'a-test-context'
            )

    def test_user_has_no_access_via_database_with_context(self):
        """
        Access check should return false if RoleAssignment does not exist for user.
        This case handles checking if the context matches.
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
            'coupon-manager:a-test-context'
        ]
        actual_claim = create_role_auth_claim_for_user(self.user)
        assert expected_claim == actual_claim
