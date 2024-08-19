"""
Tests for the `edx-rbac` utilities module.
"""

from contextlib import contextmanager
from unittest import mock

import ddt
from django.contrib import auth
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase, override_settings
from jwt.exceptions import InvalidTokenError

from edx_rbac.constants import ALL_ACCESS_CONTEXT, IGNORE_INVALID_JWT_COOKIE_SETTING
from edx_rbac.utils import (
    _user_has_access,
    contexts_accessible_from_request,
    create_role_auth_claim_for_user,
    get_decoded_jwt,
    has_access_to_all,
    is_iterable,
    request_user_has_implicit_access_via_jwt,
    set_from_collection_or_single_item,
    user_has_access_via_database
)
from tests.models import (
    ConcreteUserRole,
    ConcreteUserRoleAssignment,
    ConcreteUserRoleAssignmentDuplicateContexts,
    ConcreteUserRoleAssignmentMultipleContexts,
    ConcreteUserRoleAssignmentNoContext
)

COUPON_MANAGEMENT_FEATURE_ROLE = 'coupon-management'
DATA_API_ACCESS_FEATURE_ROLE = 'data_api_access'
User = auth.get_user_model()


@ddt.ddt
class TestUtils(TestCase):
    """
    TestUtils tests.

    Note that our test_settings.py file defines:

    SYSTEM_TO_FEATURE_ROLE_MAPPING = {
        'enterprise_admin': ['coupon-management', 'data_api_access'],
        'enterprise_leaner': [],
        'coupon-manager': ['coupon-management'],
        'enterprise_openedx_operator': ['enterprise_data_admin'],
    }

    So there is a 'coupon-manager' system-wide role which includes the
    'coupon-management' feature role in this particular system.
    """

    def setUp(self):
        super().setUp()
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

        # From the JWT, determine if I have the 'coupon-management' feature role,
        # which I should, because the JWT says I have the 'coupon-manager' system-wide role.
        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            COUPON_MANAGEMENT_FEATURE_ROLE,
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
            COUPON_MANAGEMENT_FEATURE_ROLE,
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
            COUPON_MANAGEMENT_FEATURE_ROLE,
            'some_context'
        )

    def test_request_user_has_implicit_access_via_jwt_with_all_access_context(self):
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
            COUPON_MANAGEMENT_FEATURE_ROLE,
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
            COUPON_MANAGEMENT_FEATURE_ROLE,
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
            COUPON_MANAGEMENT_FEATURE_ROLE,
            'some_context'
        )

        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            COUPON_MANAGEMENT_FEATURE_ROLE,
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
            COUPON_MANAGEMENT_FEATURE_ROLE,
            'some_context'
        )

        assert request_user_has_implicit_access_via_jwt(
            toy_decoded_jwt,
            COUPON_MANAGEMENT_FEATURE_ROLE,
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
            COUPON_MANAGEMENT_FEATURE_ROLE,
            'some_totally_different_context'
        )

    @ddt.data(
        ([COUPON_MANAGEMENT_FEATURE_ROLE, DATA_API_ACCESS_FEATURE_ROLE], {'some_context', 'some_other_context'}),
        # The 'coupon-management' feature role is provided by both system roles granted in our toy JWT.
        ([COUPON_MANAGEMENT_FEATURE_ROLE], {'some_context', 'some_other_context'}),
        # The 'data_api_access' feature role is provided only by the 'enterprise_admin' system role
        # granted in the toy JWT.
        ([DATA_API_ACCESS_FEATURE_ROLE], {'some_other_context'}),
        ([], set()),
        (['not-a-feature-role', DATA_API_ACCESS_FEATURE_ROLE], {'some_other_context'}),
        (['not-a-feature-role'], set()),
    )
    @ddt.unpack
    def test_contexts_accessible_from_request(self, role_names, expected_contexts):
        """
        For various role names, `contexts_accessible_from_request()` should grant access to certain contexts.
        """
        toy_decoded_jwt = {
            "roles": [
                "coupon-manager:some_context",  # provides the 'coupon-management' feature role
                "enterprise_admin:some_other_context",  # provides the 'data_api_access' feature role
            ]
        }
        with mock.patch('edx_rbac.utils.get_decoded_jwt', return_value=toy_decoded_jwt):
            request = mock.Mock()
            assert expected_contexts == contexts_accessible_from_request(request, role_names)

    @ddt.data(
        [COUPON_MANAGEMENT_FEATURE_ROLE, DATA_API_ACCESS_FEATURE_ROLE],
        [],
        [COUPON_MANAGEMENT_FEATURE_ROLE],
        [DATA_API_ACCESS_FEATURE_ROLE],
        ['not-a-feature-role', DATA_API_ACCESS_FEATURE_ROLE],
        ['not-a-feature-role'],
    )
    def test_contexts_accessible_from_request_with_no_jwt_roles(self, role_names):
        """
        No contexts should ever be accessible from a JWT if the JWT provides no roles.
        """
        toy_decoded_jwt = {
            "roles": []
        }
        with mock.patch('edx_rbac.utils.get_decoded_jwt', return_value=toy_decoded_jwt):
            request = mock.Mock()
            assert set() == contexts_accessible_from_request(request, role_names)

    @ddt.data(
        {'a_function': list, 'expected_value': True},
        {'a_function': str, 'expected_value': True},
        {'a_function': set, 'expected_value': True},
        {'a_function': dict, 'expected_value': True},
        {'a_function': tuple, 'expected_value': True},
        {'a_function': int, 'expected_value': False},
        {'a_function': float, 'expected_value': False},
        {'a_function': bool, 'expected_value': False},
        {'a_function': bytes, 'expected_value': True},
        {'a_function': lambda: None, 'expected_value': False},
    )
    @ddt.unpack
    def test_is_iterable(self, a_function, expected_value):
        assert expected_value == is_iterable(a_function())

    @ddt.data(
        {'obj': None,
         'expected_value': {None}},
        {'obj': 'abcabc',
         'expected_value': {'abcabc'}},
        {'obj': '',
         'expected_value': {''}},
        {'obj': 'a',
         'expected_value': {'a'}},
        {'obj': ['a', 'b', 'b'],
         'expected_value': {'a', 'b'}},
        {'obj': {'a', 'b', 'd'},
         'expected_value': {'a', 'b', 'd'}},
        {'obj': {'a': 1, 'b': 2, 'c': 3},
         'expected_value': {'a', 'b', 'c'}},
        {'obj': ('a', 'b', 'c', 'c'),
         'expected_value': {'a', 'b', 'c'}},
        {'obj': [None],
         'expected_value': {None}},
        {'obj': ((1, 2), (3, 4)),
         'expected_value': {(1, 2), (3, 4)}},  # tuples are hashable, and can be elements of a set
    )
    @ddt.unpack
    def test_set_from_collection_or_single_item(self, obj, expected_value):
        assert expected_value == set_from_collection_or_single_item(obj)

    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_auth', return_value=None)
    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_cookie')
    def test_get_decoded_jwt_when_it_exists_in_cookie(self, mock_jwt_from_cookie, mock_jwt_from_auth):
        request = mock.Mock()

        assert mock_jwt_from_cookie.return_value == get_decoded_jwt(request)

        mock_jwt_from_auth.assert_called_once_with(request)
        mock_jwt_from_cookie.assert_called_once_with(request)

    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_auth')
    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_cookie', return_value=None)
    def test_get_decoded_jwt_when_it_exists_only_in_auth(self, mock_jwt_from_cookie, mock_jwt_from_auth):
        request = mock.Mock()

        assert mock_jwt_from_auth.return_value == get_decoded_jwt(request)

        self.assertFalse(mock_jwt_from_cookie.called)
        mock_jwt_from_auth.assert_called_once_with(request)

    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_auth', return_value=None)
    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_cookie', return_value=None)
    def test_get_decoded_jwt_defaults_to_empty_dict(self, mock_jwt_from_cookie, mock_jwt_from_auth):
        request = mock.Mock()

        assert {} == get_decoded_jwt(request)

        mock_jwt_from_cookie.assert_called_once_with(request)
        mock_jwt_from_auth.assert_called_once_with(request)

    @override_settings(**{IGNORE_INVALID_JWT_COOKIE_SETTING: True})
    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_auth', return_value=None)
    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_cookie')
    def test_get_decoded_jwt_ignores_invalid_token_errors(self, mock_jwt_from_cookie, mock_jwt_from_auth):
        request = mock.Mock()
        mock_jwt_from_cookie.side_effect = InvalidTokenError('foo')

        assert {} == get_decoded_jwt(request)

        mock_jwt_from_cookie.assert_called_once_with(request)
        mock_jwt_from_auth.assert_called_once_with(request)

    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_auth', return_value=None)
    @mock.patch('edx_rbac.utils.get_decoded_jwt_from_cookie')
    def test_get_decoded_jwt_raises_invalid_token_errors_by_default(self, mock_jwt_from_cookie, mock_jwt_from_auth):
        request = mock.Mock()
        mock_jwt_from_cookie.side_effect = InvalidTokenError('foo')

        with self.assertRaises(InvalidTokenError):
            get_decoded_jwt(request)

        mock_jwt_from_cookie.assert_called_once_with(request)
        mock_jwt_from_auth.assert_called_once_with(request)

    @ddt.data(
        ({}, False),
        ({ALL_ACCESS_CONTEXT}, True),
        ({1, 2, 3, 4, 5}, False),
        ({1, 2, 3, 4, ALL_ACCESS_CONTEXT}, True),
    )
    @ddt.unpack
    def test_has_access_to_all(self, assigned_contexts, expected_result):
        assert expected_result == has_access_to_all(assigned_contexts)

    @ddt.data(
        {'assigned_contexts': {},
         'requested_contexts': {},
         'expected_result': False},  # regardless of requested contexts, if none are assigned, return False
        {'assigned_contexts': {},
         'requested_contexts': {'anything'},
         'expected_result': False},  # ditto
        {'assigned_contexts': {'anything'},
         'requested_contexts': {},
         'expected_result': True},  # if at least one context is assigned and none are requested, return True
        {'assigned_contexts': {1, 2, 3},
         'requested_contexts': {2, 3},
         'expected_result': True},  # requested is a strict subset of assigned -> True
        {'assigned_contexts': {1, 2, 3},
         'requested_contexts': {1, 2, 3},
         'expected_result': True},  # requested == assigned -> True
        {'assigned_contexts': {ALL_ACCESS_CONTEXT},
         'requested_contexts': {'anything'},
         'expected_result': True},  # wildcard is in assigned_contexts -> True
        {'assigned_contexts': {1, 2},
         'requested_contexts': {1, 2, 3},
         'expected_result': False},  # requested has more than assigned -> False
    )
    @ddt.unpack
    def test_user_has_access(self, assigned_contexts, requested_contexts, expected_result):
        assert expected_result == _user_has_access(assigned_contexts, requested_contexts)


@ddt.ddt
class TestUtilsWithDatabaseRequirements(TestCase):
    """
    TestUtilsWithDatabaseRequirements tests.
    """

    def setUp(self):
        super().setUp()
        self.user = User.objects.get_or_create(username='test_user', password='pw')[0]
        self.role = ConcreteUserRole.objects.get_or_create(name='coupon-manager')[0]

    @contextmanager
    def _create_assignment(self, assignment_cls):
        """ Helper to create assignments of various types for this object's user and role. """
        assignment = assignment_cls.objects.create(
            user=self.user,
            role=self.role,
        )
        try:
            yield
        finally:
            assignment.delete()

    @contextmanager
    def create_user_role_assignment(self):
        """ Helper to create an assignment for this object's user and role. """
        with self._create_assignment(ConcreteUserRoleAssignment):
            yield

    @contextmanager
    def create_user_role_assignment_multiple_contexts(self):
        """ Helper to create a "Multiple Context" assignment for this object's user and role. """
        with self._create_assignment(ConcreteUserRoleAssignmentMultipleContexts):
            yield

    @contextmanager
    def create_user_role_assignment_duplicate_contexts(self):
        """ Helper to create a "Duplicate Context" assignment for this object's user and role. """
        with self._create_assignment(ConcreteUserRoleAssignmentDuplicateContexts):
            yield

    @contextmanager
    def create_user_role_assignment_no_context(self):
        """ Helper to create a "No Context" assignment for this object's user and role. """
        with self._create_assignment(ConcreteUserRoleAssignmentNoContext):
            yield

    def test_user_has_access_via_database(self):
        """
        Access check should return true if RoleAssignment exists for user
        """
        with self.create_user_role_assignment():
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
        with self.create_user_role_assignment():
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
        with self.create_user_role_assignment_multiple_contexts():
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
        with self.create_user_role_assignment(), mock.patch(
                'tests.models.ConcreteUserRoleAssignment.get_context', return_value=ALL_ACCESS_CONTEXT
        ):
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
        with self.create_user_role_assignment_multiple_contexts(), mock.patch(
                'tests.models.ConcreteUserRoleAssignmentMultipleContexts.get_context',
                return_value=['some_context', ALL_ACCESS_CONTEXT]
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
        with self.create_user_role_assignment():
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
        with self.create_user_role_assignment_multiple_contexts():
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
        with self.create_user_role_assignment_no_context():
            assert not user_has_access_via_database(
                self.user,
                'coupon-manager',
                ConcreteUserRoleAssignment,
                'not_the_right_context'
            )

    def test_anonymous_user_has_no_access_via_database(self):
        """
        Access check should return false if user is an AnonymousUser object
        """
        user = AnonymousUser()
        assert not user_has_access_via_database(
            user,
            'coupon-manager',
            ConcreteUserRoleAssignment,
            'test_context'
        )

    def test_create_role_auth_claim_for_user(self):
        """
        Helper function should create a list of strings based on the roles
        associated with the user.
        """
        with self.create_user_role_assignment():
            expected_claim = [
                'coupon-manager:a-test-context',
                'test-role',
                'test-role2:1',
            ]
            actual_claim = create_role_auth_claim_for_user(self.user)
            self.assertCountEqual(expected_claim, actual_claim)

    @ddt.data(
        'create_user_role_assignment_duplicate_contexts',
        'create_user_role_assignment_multiple_contexts',
    )
    def test_create_role_auth_claim_for_user_with_many_contexts(self, role_assignment_context_manager_name):
        """
        Helper function should create a list of strings based on the roles
        associated with the user with multiple contexts, and it should
        always be a list of unique items.
        """
        role_assignment_context_manager = getattr(self, role_assignment_context_manager_name)
        with role_assignment_context_manager():
            expected_claim = [
                'coupon-manager:a-test-context',
                'coupon-manager:a-second-test-context',
                'test-role',
                'test-role2:1',
            ]
            actual_claim = create_role_auth_claim_for_user(self.user)
            self.assertCountEqual(expected_claim, actual_claim)
