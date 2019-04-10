"""
This is an example of a function-based role retriever.
"""
from __future__ import absolute_import, unicode_literals


def get_assigments(user):
    """
    Return iterator of (role_name, context)
    """
    yield 'test-role', None
    yield 'test-role2', str(user.id)
