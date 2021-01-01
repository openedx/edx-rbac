"""
Utils for 'edx-rbac' module.
"""

import importlib
from collections import defaultdict
from collections.abc import Iterable

from django.apps import apps
from django.conf import settings
from edx_rest_framework_extensions.auth.jwt.authentication import get_decoded_jwt_from_auth
from edx_rest_framework_extensions.auth.jwt.cookies import get_decoded_jwt as get_decoded_jwt_from_cookie

ALL_ACCESS_CONTEXT = '*'


def request_user_has_implicit_access_via_jwt(decoded_jwt, role_name, context=None):
    """
    Check the request's user access by mapping user's roles found in jwt to local feature roles.

    decoded_jwt is a dict
    role_name is a string
    context is anything

    Returns a boolean.

    Mapping should be in settings and look like:

        SYSTEM_TO_FEATURE_ROLE_MAPPING = {
            'enterprise_admin': ['coupon-management', 'data_api_access'],
            'enterprise_leaner': [],
            'coupon-manager': ['coupon-management']
        }
    """
    if not decoded_jwt:
        return False

    assigned_contexts = contexts_accessible_from_jwt(decoded_jwt, [role_name])
    return _user_has_access(assigned_contexts, context)


def contexts_accessible_from_request(request, role_names):
    """
    Uses the JWT provided from a given `request` to determine
    the set of accessible contexts for the given `role_name`.

    This answers the question: What are all of the contexts accessible to the
    requesting user under the given role via the request's JWT?
    """
    return contexts_accessible_from_jwt(
        get_decoded_jwt(request),
        role_names
    )


def contexts_accessible_from_jwt(decoded_jwt, role_names):
    """
    Given a `decoded_jwt` dictionary and a list of role names,
    returns a set of contexts (identifiers) to which the JWT
    grants access for the given roles.  May contain the "wildcard" `ALL_ACCESS_CONTEXT`,
    which grants access within these roles to any context.
    """
    assigned_contexts_by_feature_role = feature_roles_from_jwt(decoded_jwt)
    accessible_contexts = set()
    for role_name in role_names:
        accessible_contexts.update(
            assigned_contexts_by_feature_role.get(role_name, [])
        )
    return accessible_contexts


def feature_roles_from_jwt(decoded_jwt):
    """
    Get the mapping of feature roles to roles found in the given JWT.

    Given a decoded JWT, returns a mapping of feature role names to list of
    contexts for which that role name applies.  A "context" here usually
    means the primary identifier of some resource.
    """
    jwt_roles_claim = decoded_jwt.get('roles', [])

    feature_roles = defaultdict(list)

    for role_data in jwt_roles_claim:
        # split should be more robust because of our cousekeys having colons
        role_in_jwt, __, context_in_jwt = role_data.partition(':')
        mapped_roles = settings.SYSTEM_TO_FEATURE_ROLE_MAPPING.get(role_in_jwt, [])
        for role in mapped_roles:
            feature_roles[role].append(context_in_jwt)

    return feature_roles


def user_has_access_via_database(user, role_name, role_assignment_class, context=None):
    """
    Check if there is a role assignment for a given user and role.

    The role object itself is found via the role_name. The role_assignment_class's get_context() method can return a
    single context string which could be an ALL_ACCESS_CONTEXT or, incase of multiple user contexts, a list of strings.
    The context argument is evaluated against the context(s) received from the role_assignment_class while accounting
    for the ALL_ACCESS_CONTEXT to grant access.
    """
    if getattr(user, 'is_anonymous', False):
        return False

    assigned_contexts = contexts_accessible_from_database(user, [role_name], role_assignment_class)
    return _user_has_access(assigned_contexts, context)


def contexts_accessible_from_database(user, role_names, role_assignment_class):
    """
    Given a user and role, returns a set of contexts (identifiers) to
    which the user has access for the role.  May contain the "wildcard" `ALL_ACCESS_CONTEXT`,
    which grants access in this role to any context.

    This answers the question: What are all of the contexts accessible to the
    requesting user under the given role via DB-persisted role assignments?
    """
    assigned_contexts = set()

    for _, context in role_assignment_class.get_assignments(user, role_names):
        assigned_contexts.update(
            set_from_collection_or_single_item(context)
        )
    return assigned_contexts


def create_role_auth_claim_for_user(user):
    """
    Create role auth claim for a given user.

    Takes a user, and for each RoleAssignment class specified in config as a
    system wide jwt role associated with that user, creates a list of strings
    denoting the role and context.

    Returns a list.

    This setting is a list of classes whose roles should be added to the
    jwt. The setting should look something like this:

        SYSTEM_WIDE_ROLE_CLASSES = [
            SystemWideConcreteUserRoleAssignment
        ]
    """
    def append_role_auth_claim(role_string, context=None):
        """
        Append the formatted auth claim for a role and context.
        """
        if context:
            contextual_role = f'{role_string}:{context}'
            role_auth_claim.append(contextual_role)
        else:
            role_auth_claim.append(role_string)

    role_auth_claim = []
    for system_role_loc in settings.SYSTEM_WIDE_ROLE_CLASSES:
        # location can either be a module or a django model
        module_name, func_name = system_role_loc.rsplit('.', 1)
        try:
            # first, assume that this is a plain function
            module = importlib.import_module(module_name)
            role_func = getattr(module, func_name)
        except (ImportError, AttributeError):
            # otherwise, assume that it's a django model
            module = apps.get_model(module_name, func_name)
            role_func = module.get_assignments

        for role_string, context in role_func(user):
            if context:
                if isinstance(context, str):
                    append_role_auth_claim(role_string, context)
                else:
                    for item in context:
                        append_role_auth_claim(role_string, item)
            else:
                append_role_auth_claim(role_string)
    return role_auth_claim


def is_iterable(obj):
    """
    Returns True if obj is an instance of collections.abc.Iterable.
    """
    return isinstance(obj, Iterable)


def set_from_collection_or_single_item(obj):
    """
    For iterables that are not strings, returns a set of the iterable.
    For all other types of objects, returns a set containing only the object.
    """
    if is_iterable(obj) and not isinstance(obj, str):
        return set(obj)
    return {obj}


def get_decoded_jwt(request):
    """
    Decodes the request's JWT from either cookies or auth payload and returns it.
    Defaults to an empty dictionary.
    """
    decoded_jwt = get_decoded_jwt_from_cookie(request) or get_decoded_jwt_from_auth(request)
    return decoded_jwt or {}


def has_access_to_all(assigned_contexts):
    """
    Determines whether the `ALL_ACCESS_CONTEXT` token is in the set of assigned contexts.
    """
    return ALL_ACCESS_CONTEXT in assigned_contexts


def _user_has_access(assigned_contexts, requested_context):
    """
    `assigned_contexts` - A set of contexts/identifiers which have been assigned access to some user.
    `requested_context` - 0 or many contexts of which to check access.
    """
    # If there are no contexts assigned, return False.
    if not assigned_contexts:
        return False

    # If the user has access to at least one context, and no particular
    # context was asked to be checked in this call, return True.
    if not requested_context:
        return True

    contexts_to_check = set_from_collection_or_single_item(requested_context)

    return has_access_to_all(assigned_contexts) or contexts_to_check.issubset(assigned_contexts)
