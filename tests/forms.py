"""
Forms to be used for testing.
"""

from edx_rbac.admin.forms import UserRoleAssignmentAdminForm
from tests.models import ConcreteUserRoleAssignment


class ConcreteUserRoleAssignmentAdminForm(UserRoleAssignmentAdminForm):
    """
    Used for testing UserRoleAssignmentAdminForm.
    """

    class Meta:
        """
        Meta class for ConcreteUserRoleAssignmentAdminForm.
        """

        model = ConcreteUserRoleAssignment
        fields = ('user', 'role')

    def cleaned_data(self):  # pylint: disable=useless-super-delegation,method-hidden
        """
        Return cleaned data.
        """
        # pylint: disable=no-member
        return super().cleaned_data()
