"""
All constants pertaining to the edx_rbac module.
"""
# The string denoting that a given role is applicable across all contexts
ALL_ACCESS_CONTEXT = '*'

# .. toggle_name: RBAC_IGNORE_INVALID_JWT_COOKIE
# .. toggle_implementation: DjangoSetting
# .. toggle_default: False
# .. toggle_description: When true, causes instances of `jwt.exceptions.InvalidTokenError`
#   to be ignored instead of raised in the `get_decoded_jwt()` utility function.
#   Defaults to False for backward-compatibility purposes, but it's recommended
#   to be set to True in dependent applications.
# .. toggle_use_cases: opt_in
# .. toggle_creation_date: 2024-08-19
IGNORE_INVALID_JWT_COOKIE_SETTING = 'RBAC_IGNORE_INVALID_JWT_COOKIE'
