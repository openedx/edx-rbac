"""
Tests for the `edx-rbac` fields module.
"""

from django.contrib import auth
from django.core.exceptions import ValidationError
from django.test import TestCase

from edx_rbac.fields import UserFromEmailField

User = auth.get_user_model()


class TestFields(TestCase):
    """
    TestFields tests.
    """

    def setUp(self):
        super().setUp()
        self.email = 'cool4eva@gmail.com'
        self.user = User.objects.create(
            username='test_user',
            password='pw',
            email=self.email,
        )

    def test_user_from_email_field_clean(self):
        """
        UserFromEmailField clean method should return User if user exists.
        """

        field = UserFromEmailField()
        assert self.user == field.clean(self.email)

    def test_user_from_email_field_clean_error(self):
        """
        UserFromEmailField clean method should throw a DoesNotExist error
        if user cannot be found.
        """

        field = UserFromEmailField()
        unassociated_email = 'whatisedx@example.com'
        with self.assertRaises(ValidationError):
            field.clean(unassociated_email)
