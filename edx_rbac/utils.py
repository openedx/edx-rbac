# -*- coding: utf-8 -*-
"""
Utils for 'edx-rbac' module.
"""
from __future__ import absolute_import, unicode_literals

import importlib

from django.apps import apps
from django.conf import settings

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
    jwt_roles_claim = decoded_jwt.get('roles', [])

    feature_roles = {}
    for role_data in jwt_roles_claim:
        # split should be more robust because of our cousekeys having colons
        role_in_jwt, __, context_in_jwt = role_data.partition(':')
        mapped_roles = settings.SYSTEM_TO_FEATURE_ROLE_MAPPING.get(role_in_jwt, [])
        feature_roles.update({role: context_in_jwt for role in mapped_roles})

    if role_name in feature_roles:
        if not context:
            return True
        else:
            return feature_roles[role_name] in (context, ALL_ACCESS_CONTEXT)

    return False


def user_has_access_via_database(user, role_name, role_assignment_class, context=None):
    """
    Check if there is a role assignment for a given user and role.

    The role object itself is found via the role_name
    """
    try:
        role_assignment = role_assignment_class.objects.get(user=user, role__name=role_name)
    except role_assignment_class.DoesNotExist:
        return False

    if context:
        return role_assignment.get_context() in (context, ALL_ACCESS_CONTEXT)

    return True


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
                role_string = '{}:{}'.format(role_string, context)
            role_auth_claim.append(role_string)
    return role_auth_claim
