"""
This is an example of a function-based role retriever.
"""


def get_assigments(user):
    """
    Return iterator of (role_name, context)
    """
    yield 'test-role', None
    yield 'test-role2', str(user.id)
