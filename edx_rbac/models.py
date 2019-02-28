# -*- coding: utf-8 -*-
"""
Database models for edx_rbac.
"""

from __future__ import absolute_import, unicode_literals

# from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from model_utils.models import TimeStampedModel


@python_2_unicode_compatible
class UserRole(TimeStampedModel):
    """
    TODO: replace with a brief description of the model.

    TODO: Add either a negative or a positive PII annotation to the end of this docstring.  For more
    information, see OEP-30:
    https://open-edx-proposals.readthedocs.io/en/latest/oep-0030-arch-pii-markup-and-auditing.html
    """

    # TODO: add field definitions

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        # TODO: return a string appropriate for the data fields
        return '<UserRole, ID: {}>'.format(self.id)


@python_2_unicode_compatible
class Role(TimeStampedModel):
    """
    TODO: replace with a brief description of the model.

    TODO: Add either a negative or a positive PII annotation to the end of this docstring.  For more
    information, see OEP-30:
    https://open-edx-proposals.readthedocs.io/en/latest/oep-0030-arch-pii-markup-and-auditing.html
    """

    # TODO: add field definitions

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        # TODO: return a string appropriate for the data fields
        return '<Role, ID: {}>'.format(self.id)
