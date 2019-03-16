# -*- coding: utf-8 -*-
"""
Tests for the `edx-rbac` utilities module.
"""
from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from tests.forms import ConcreteUserRoleAssignmentAdminForm
from tests.models import ConcreteUserRole, ConcreteUserRoleAssignment
from edx_rbac.admin.forms import UserFromEmailField


class TestForms(TestCase):
    """
    TestForms tests.
    """

    def setUp(self):
        super(TestForms, self).setUp()
        self.email = 'cool4eva@gmail.com'
        self.user = User.objects.create(
            username='test_user',
            password='pw',
            email=self.email,
        )
        self.role = ConcreteUserRole(name='coupon-manager')
        self.role.save()

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

    def test_user_role_assignment_form(self):
        """
        When UserRoleAssignmentAdminForm is initialized and saved, a RoleAssignment
        object is created.
        """

        assert ConcreteUserRoleAssignment.objects.count() == 0
        # Role exists underneath the hood as something like: (1, u'coupon-manager')
        data = {
            'user': self.email,
            'role': 1,  
        }
        form = ConcreteUserRoleAssignmentAdminForm(data=data)
        assert form.is_valid()
        form.save()
        assert ConcreteUserRoleAssignment.objects.count() == 1

    def test_user_role_assignment_form_init_with_instance(self):
        """
        When UserRoleAssignmentAdminForm is initialized with instance, the proper values
        are set.
        """

        assert ConcreteUserRoleAssignment.objects.count() == 0
        user2 = User.objects.create(
            username='test_user2',
            password='pw2',
            email='{}2'.format(self.email),
        )
        role_assignment = ConcreteUserRoleAssignment.objects.create(
            user=user2,
            role=self.role
        )
        # Django docs state "if initial was provided, it should override
        # the values from instance", but custom init in our form will replace
        # the initial dict's user value with the instance's useremail, if an instance
        # is provided
        initial = {
            'user': self.email,
            'role': 1,  
        }
        form = ConcreteUserRoleAssignmentAdminForm(initial=initial, instance=role_assignment)
        form.is_valid()
        form.save()

        assert form.initial['user'] == user2.email
        assert ConcreteUserRoleAssignment.objects.count() == 1
