"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'edx_rbac',
    'tests',
)

LOCALE_PATHS = [
    root('edx_rbac', 'conf', 'locale'),
]

ROOT_URLCONF = 'edx_rbac.urls'

SECRET_KEY = 'insecure-secret-key'

SITE_NAME = 'testserver'

SYSTEM_TO_FEATURE_ROLE_MAPPING = {
    'enterprise_admin': ['coupon-management', 'data_api_access'],
    'enterprise_leaner': [],
    'coupon-manager': ['coupon-management'],
    'enterprise_openedx_operator': ['enterprise_data_admin'],
}

SYSTEM_WIDE_ROLE_CLASSES = [
    'tests.ConcreteUserRoleAssignment',
    'tests.ConcreteUserRoleAssignmentMultipleContexts',
    'tests.test_assignments.get_assigments',
]

AUTH_USER_MODEL = 'auth.User'

# Required for use with edx-drf-extensions JWT functionality:
# USER_SETTINGS overrides for djangorestframework-jwt APISettings class
# See https://github.com/GetBlimp/django-rest-framework-jwt/blob/master/rest_framework_jwt/settings.py
JWT_AUTH = {

    'JWT_AUDIENCE': 'test-aud',

    'JWT_DECODE_HANDLER': 'edx_rest_framework_extensions.auth.jwt.decoder.jwt_decode_handler',

    'JWT_ISSUER': 'test-iss',

    'JWT_LEEWAY': 1,

    'JWT_SECRET_KEY': 'test-key',

    'JWT_SUPPORTED_VERSION': '1.0.0',

    'JWT_VERIFY_AUDIENCE': False,

    'JWT_VERIFY_EXPIRATION': True,

    # JWT_ISSUERS enables token decoding for multiple issuers (Note: This is not a native DRF-JWT field)
    # We use it to allow different values for the 'ISSUER' field, but keep the same SECRET_KEY and
    # AUDIENCE values across all issuers.
    'JWT_ISSUERS': [
        {
            'ISSUER': 'test-issuer-1',
            'SECRET_KEY': 'test-secret-key',
            'AUDIENCE': 'test-audience',
        },
        {
            'ISSUER': 'test-issuer-2',
            'SECRET_KEY': 'test-secret-key',
            'AUDIENCE': 'test-audience',
        }
    ],
}
