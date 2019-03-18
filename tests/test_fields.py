# -*- coding: utf-8 -*-
"""
Tests for the `edx-rbac` fields module.
"""
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from edx_rbac.fields import UserFromEmailField


class TestFields(TestCase):
    """
    TestFields tests.
    """

    def setUp(self):
        super(TestFields, self).setUp()
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
