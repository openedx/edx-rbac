# -*- coding: utf-8 -*-
"""
Forms to be used for testing.
"""

from edx_rbac.admin.forms import UserFromEmailField, UserRoleAssignmentAdminForm
from tests.models import ConcreteUserRoleAssignment

class ConcreteUserRoleAssignmentAdminForm(UserRoleAssignmentAdminForm):
    """
    Used for testing UserRoleAssignmentAdminForm.
    """
    def cleaned_data(self):
    	super(ConcreteUserRoleAssignmentAdminForm, self).cleaned_data()
    
    class Meta:
    	model = ConcreteUserRoleAssignment
    	fields = ('user', 'role')
