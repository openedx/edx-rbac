"""
Taken from https://github.com/escodebar/django-rest-framework-rules/blob/master/rest_framework_rules/decorators.py.
"""

import functools

import crum


def permission_required(*permissions, **decorator_kwargs):
    """
    Verify permissions for access to the api.

    :param permissions: Permissions added via django_rules add_perm
    :param decorator_kwargs: Arguments for permission checks
    :return: decorator
    """
    def decorator(view):
        """Verify permissions decorator."""
        @functools.wraps(view)
        def wrapped_view(self, request, *args, **kwargs):
            """Wrap for the view function."""
            fn = decorator_kwargs.get('fn', None)
            if callable(fn):
                obj = fn(request, *args, **kwargs)
            else:
                obj = fn

            crum.set_current_request(request)

            missing_permissions = [perm for perm in permissions
                                   if not request.user.has_perm(perm, obj)]
            if any(missing_permissions):
                # raises a permission denied exception causing a 403 response
                self.permission_denied(
                    request,
                    message=f"Missing: {', '.join(missing_permissions)}"
                )

            return view(self, request, *args, **kwargs)
        return wrapped_view

    return decorator
