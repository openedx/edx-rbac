"""
Mixin adapted from https://github.com/escodebar/django-rest-framework-rules/blob/master/rest_framework_rules/mixins.py.

Keeps py2 backward compatibility and only holds on to the necessary bits of the mixin needed.
"""

import crum
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property

from edx_rbac import utils


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
        if isinstance(self.permission_required, str):
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


class PermissionRequiredForListingMixin(PermissionRequiredMixin):
    """
    Mixin for checking role-based access against multiple objects, specifically
    using the "list" action of a DRF ViewSet.  The brunt of the work is done in
    the `accessible_contexts` cached property - this property determines the set
    of "contexts" (probably identifiers of some model) to which the requesting
    user has access under any of the `allowed_roles`.  It's pretty opinionated and
    you _must_ define the following fields:

    `list_lookup_field` (string) - The field of the model you want to list instances of
    that holds values defined by `accessible_contexts`.

    `allowed_roles` (list) - A list of one or more roles against which access is checked.  It's disjunctive,
    which means that if "role_1" grants access to resources "A" and "B", and
    "role_2" grants access to resource "C", defining `allowed_roles = ['role_1', 'role_2']`
    will cause resources "A", "B", and "C" to be returned by a listing operation
    for a user who is granted both "role_1" and "role_2".

    `role_assignment_class` (class) - The RoleAssignmentClass against which DB-defined access is checked.

    `base_queryset` (property) - A queryset which acts as the "base case".  It should generally return
    all accessible instances for a user who has access to anything within this viewset (like a superuser
    or admin).
    """
    # This flag indicates whether requesting users with `is_staff = True`
    # should ever encounter a PermissionDenied exception.
    staff_are_never_forbidden = True

    # This flag indicates whether requesting users with `is_superuser = True`
    # should always have the `ALL_ACCESS_CONTEXT` included in their set of accessible contexts.
    superusers_can_access_anything = True

    # The field (as a string) of the model you want to list instances of.
    list_lookup_field = None

    # A list of one or more roles against which access is checked.
    allowed_roles = []

    # The RoleAssignmentClass against which DB-defined access is checked
    role_assignment_class = None

    @property
    def base_queryset(self):
        """
        Should return a queryset that acts as the "base case".
        It should generally return all accessible instances for a user who has access
        to everything within this viewset (like a superuser or admin).
        """
        raise NotImplementedError

    @cached_property
    def request_action(self):
        """
        Returns `self.action` if it exists, None otherwise.
        """
        return getattr(self, 'action', None)

    @cached_property
    def accessible_contexts(self):
        """
        Cached set of contexts (usually model identifiers) the requesting user has access to.
        Returns a set that contains the `ALL_ACCESS_CONTEXT` identifier
        if the requesting user is a superuser.
        """
        contexts_via_jwt = utils.contexts_accessible_from_request(self.request, self.allowed_roles)
        contexts_via_db = set()

        if self.role_assignment_class:
            contexts_via_db = utils.contexts_accessible_from_database(
                self.request.user, self.allowed_roles, self.role_assignment_class
            )

        if self.request.user.is_superuser and self.superusers_can_access_anything:
            contexts_via_db.add(utils.ALL_ACCESS_CONTEXT)

        return contexts_via_jwt | contexts_via_db

    def check_permissions(self, request):
        """
        If dealing with a "list" action, goes through some customized
        logic to check which contexts are accessible by the requesting
        user.  If none are, and the user is not staff/super, raise
        a `PermissionDenied` exception.  Uses the parent class's `check_permissions()`
        method if the request action is not "list".
        """
        if self.request_action == 'list':
            # Super-users and staff won't get Forbidden responses,
            # but depending on their assigned roles, staff may
            # get an empty result set.
            if request.user.is_superuser:
                return
            if request.user.is_staff and self.staff_are_never_forbidden:
                return
            if not self.accessible_contexts:
                self.permission_denied(request)
        else:
            super().check_permissions(request)

    def get_queryset(self):
        """
        Expects `self.base_queryset` to be explicitly defined as the "base case"
        and `self.list_lookup_field` to be defined.
        You'll most likely want it to be `MyModel.objects.all().order_by('some_field')`.
        """
        if getattr(self, 'base_queryset', None) is None:
            raise Exception(f'{self.__class__} must have a non-null "base_queryset" field.')
        if not getattr(self, 'list_lookup_field', None):
            raise Exception(f'{self.__class__} must have a truthy "list_lookup_field" field.')

        if self.request_action == 'list':
            if not self.accessible_contexts:
                return self.base_queryset.none()
            if utils.has_access_to_all(self.accessible_contexts):
                return self.base_queryset
            kwargs = {self.list_lookup_field + '__in': self.accessible_contexts}
            return self.base_queryset.filter(**kwargs)

        return self.base_queryset
