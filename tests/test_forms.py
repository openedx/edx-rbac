"""
Tests for the `edx-rbac` forms module.
"""

from django.contrib import auth
from django.test import TestCase

from tests.forms import ConcreteUserRoleAssignmentAdminForm
from tests.models import ConcreteUserRole, ConcreteUserRoleAssignment

User = auth.get_user_model()


class TestForms(TestCase):
    """
    TestForms tests.
    """

    def setUp(self):
        super().setUp()
        self.email = 'cool4eva@gmail.com'
        self.user = User.objects.create(
            username='test_user',
            password='pw',
            email=self.email,
        )
        self.role = ConcreteUserRole(name='coupon-manager')
        self.role.save()

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
            email=f'{self.email}2',
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
