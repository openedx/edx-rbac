"""
Forms to be used for djangoapps extending edx_rbac.
"""

from django import forms
from django.utils.translation import ugettext as _

from edx_rbac.fields import UserFromEmailField


class UserRoleAssignmentAdminForm(forms.ModelForm):
    """
    Custom Form for CRUD operations on models extending UserRoleAssignment.
    """
    user = UserFromEmailField(
        label=_('User Email'),
        required=True
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})
        if instance:
            initial['user'] = instance.user.email
            kwargs['initial'] = initial
        super().__init__(*args, **kwargs)
