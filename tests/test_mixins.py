"""
Tests for the `edx-rbac` mixins module.
"""

from unittest import mock

import ddt
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from edx_rbac.mixins import PermissionRequiredForListingMixin
from edx_rbac.utils import ALL_ACCESS_CONTEXT


class ToyRoleAssignmentClass:
    """
    Provides no functionality.
    """


class ToyViewSet(PermissionRequiredForListingMixin):
    """
    Toy class for testing permissions around list endpoints.
    """
    list_lookup_field = 'some_field'
    allowed_roles = ['role_1', 'role_2']
    role_assignment_class = ToyRoleAssignmentClass

    request = mock.MagicMock()
    action = 'list'

    base_queryset = mock.MagicMock()
    # Falsey (empty) QuerySets are allowed
    base_queryset.__bool__.return_value = False

    def permission_denied(self, request):
        raise PermissionDenied


class ToyViewSetNullBaseQueryset(PermissionRequiredForListingMixin):
    """
    Toy class for testing that an exception is raised
    when base_queryset returns None.
    """
    list_lookup_field = 'something'
    allowed_roles = ['role_1', 'role_2']
    role_assignment_class = ToyRoleAssignmentClass

    request = mock.MagicMock()
    action = 'list'

    base_queryset = None  # should raise an AssertionError

    def permission_denied(self, request):
        raise PermissionDenied


class ToyViewSetEmptyListLookupField(PermissionRequiredForListingMixin):
    """
    Toy class for testing that an exception is raised
    when base_queryset returns None.
    """
    list_lookup_field = 'something'
    allowed_roles = ['role_1', 'role_2']
    role_assignment_class = ToyRoleAssignmentClass

    request = mock.MagicMock()
    action = 'list'

    base_queryset = None  # should raise an AssertionError

    def permission_denied(self, request):
        raise PermissionDenied


@ddt.ddt
class TestPermissionRequiredForListingMixin(TestCase):
    """
    Tests for the `PermissionRequiredForListingMixin` mixin.

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

    @mock.patch('edx_rbac.mixins.utils.contexts_accessible_from_request', return_value=set())
    @mock.patch('edx_rbac.mixins.utils.contexts_accessible_from_database', return_value=set())
    # pylint: disable=unused-argument
    def test_accessible_contexts_superuser(self, mock_contexts_from_request, mock_contexts_from_database):
        """
        Superusers get access to all contexts if the `superusers_can_access_anything` switch is on.
        """
        viewset = ToyViewSet()
        viewset.request.user.is_superuser = True

        assert {ALL_ACCESS_CONTEXT} == viewset.accessible_contexts

    @mock.patch('edx_rbac.mixins.utils.contexts_accessible_from_request', return_value=set())
    @mock.patch('edx_rbac.mixins.utils.contexts_accessible_from_database', return_value=set())
    # pylint: disable=unused-argument
    def test_accessible_contexts_superuser_not_granted_all_contexts(
            self, mock_contexts_from_request, mock_contexts_from_database
    ):
        """
        Toggling the `superusers_can_access_anything` switch off means superusers
        don't automatically get access to all contexts.
        """
        viewset = ToyViewSet()
        viewset.superusers_can_access_anything = False
        viewset.request.user.is_superuser = True

        assert set() == viewset.accessible_contexts

    @ddt.data(
        (set(), set()),
        ({'context-a'}, {'context-b'}),
        ({'context-a', 'context-b'}, set()),
        (set(), {'context-a', 'context-b'}),
    )
    @ddt.unpack
    def test_accessible_contexts_non_superusers(self, contexts_from_jwt, contexts_from_db):
        """
        For non-superusers, `contexts_accessible_from_request` and `contexts_accessible_from_database`
        determine the set of accessible contexts for a user.
        """
        viewset = ToyViewSet()
        viewset.request.user.is_superuser = False

        with mock.patch(
            'edx_rbac.mixins.utils.contexts_accessible_from_request', autospec=True, return_value=contexts_from_jwt
        ) as mock_contexts_accessible_from_request, mock.patch(
            'edx_rbac.mixins.utils.contexts_accessible_from_database', autospec=True, return_value=contexts_from_db
        ) as mock_contexts_accessible_from_database:

            assert contexts_from_jwt | contexts_from_db == viewset.accessible_contexts
            assert ALL_ACCESS_CONTEXT not in viewset.accessible_contexts

            mock_contexts_accessible_from_request.assert_called_once_with(
                viewset.request, viewset.allowed_roles
            )
            mock_contexts_accessible_from_database.assert_called_once_with(
                viewset.request.user, viewset.allowed_roles, viewset.role_assignment_class
            )

    @ddt.data(
        (True, False),
        (False, True)
    )
    @ddt.unpack
    def test_check_permissions_list_superuser_and_staff_never_forbidden(self, is_superuser, is_staff):
        """
        No PermissionDenied exception is raised for superusers
        or staff (when the `staff_are_never_forbidden` flag is True)
        who request to list resources.
        """
        viewset = ToyViewSet()
        viewset.staff_are_never_forbidden = True

        request = RequestFactory().get('/')
        request.user = mock.Mock(is_superuser=is_superuser, is_staff=is_staff)

        assert viewset.check_permissions(request) is None

    def test_check_permissions_list_staff_can_be_forbidden(self):
        """
        A PermissionDenied exception is raised for staff who request to list resources
        when the `staff_are_never_forbidden` flag is False and no contexts are accessible.
        """
        viewset = ToyViewSet()
        viewset.staff_are_never_forbidden = False
        viewset.accessible_contexts = set()

        request = RequestFactory().get('/')
        request.user = mock.Mock(is_superuser=False, is_staff=True)

        with self.assertRaises(PermissionDenied):
            viewset.check_permissions(request)

    def test_get_queryset_list_no_accessible_contexts(self):
        """
        An empty queryset is returned when no contexts are accessible.
        """
        viewset = ToyViewSet()
        viewset.accessible_contexts = set()

        actual_queryset = viewset.get_queryset()
        expected_queryset = viewset.base_queryset.none()

        assert expected_queryset == actual_queryset

    def test_get_queryset_list_all_accessible_contexts(self):
        """
        The base queryset is returned when all contexts are accessible.
        """
        viewset = ToyViewSet()
        viewset.accessible_contexts = {ALL_ACCESS_CONTEXT}

        actual_queryset = viewset.get_queryset()
        expected_queryset = viewset.base_queryset

        assert expected_queryset == actual_queryset

    def test_get_queryset_list_some_accessible_contexts(self):
        """
        A filtered queryset is returned when some contexts are accessible.
        """
        viewset = ToyViewSet()
        viewset.accessible_contexts = {'context-a', 'context-b'}

        actual_queryset = viewset.get_queryset()
        expected_queryset = viewset.base_queryset.filter(
            some_field__in=['context-a', 'context-b']
        )

        assert expected_queryset == actual_queryset

    def test_get_queryset_detail_returns_base_queryset(self):
        """
        The base queryset is returned when requesting an action other than 'list'.
        """
        viewset = ToyViewSet()
        viewset.accessible_contexts = {ALL_ACCESS_CONTEXT}
        viewset.action = 'detail'

        actual_queryset = viewset.get_queryset()
        expected_queryset = viewset.base_queryset

        assert expected_queryset == actual_queryset

    def test_get_queryset_assertion_error_for_null_base_queryset(self):
        """
        The get_queryset() method should raise an exception
        if the base_queryset property is null.
        """
        viewset = ToyViewSetNullBaseQueryset()
        with self.assertRaises(Exception):
            viewset.get_queryset()

    def test_get_queryset_assertion_error_for_empty_list_lookup_field(self):
        """
        The get_queryset() method should raise an exception
        if the list_lookup_field is empty.
        """
        viewset = ToyViewSetEmptyListLookupField()
        with self.assertRaises(Exception):
            viewset.get_queryset()
