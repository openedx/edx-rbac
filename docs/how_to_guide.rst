RBAC authorization guide
========================
This guide covers information you need to know to implement role-based authorization on API endpoints.


.. contents:: Table of Contents

Background
----------
What is a role? What do "access" and "authorization" even mean?  This section provides a brief
outline of how Role-Based Access Control (RBAC).


The Big Idea
^^^^^^^^^^^^
There are many different types of users within the Open edX ecosystem, for example: a learner in a course,
a course author, a course administrator, an enterprise administrator, or a global administrator. We often
want to restrict access to certain resources based on the type of user requesting access to those resources.
A "role" is simply a synonym for "type of user".  In edx-rbac, we provide utilities to define a mapping
of users to roles (that is, we can specify that "jane" has the role "enterprise administrator").

Similarly, there are many different types of permissions that may be applicable to some type of resource, for example:
permission to read data about some resource, permission to update a resource, etc.  Django allows
us to define permissions at the model (type of resource) or object (a specific instance of a model).

We can make use of a library called `django-rules <https://github.com/dfunckt/django-rules>`_ to define "predicates",
which are boolean functions that answer "is this resource accessible in a certain to the requesting user?"
These predicates can be defined based on a user's role. `django-rules` then allows us to map predicates to
a Django permission.

This is all pretty straightforward.  The complexity lies in the fact that the
Open edX ecosystem ("the ecosystem" hereafter) is composed
of discrete micro-services and micro-frontends. The edx-rbac solution to this complexity is to define
two different types of roles and let each service specify a mapping between them.


Central Authentication Service
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The LMS service (that is, ``courses.edx.org``) is the central Authentication provider in the Open edX ecosystem. It
provides authenticated users with a JSON Web Token (JWT) in the form of a cookie.  This JWT specifies the set of
roles that are applicable to the user throughout the ecosystem.
See `OEP-42: Authentication <https://open-edx-proposals.readthedocs.io/en/latest/oep-0042-bp-authentication.html>`_
for a broader overview of Authentication.


Roles
^^^^^
edx-rbac makes use of two types of roles:

* System wide roles: These are the roles used across the ecosystem.
  Role data is added to an authenticated user's JWT cookie based on `assignment` relationships between
  the user, a role, and a context (which is usually a resource identifier).  This assignment is usually
  persisted using a Django model.

* Feature specific roles:
    These are specific to a feature/service.  They may be inferred based on an assigned system-wide role,
    or declared explicitly via an assignment relationship.

Access
^^^^^^
* Implicit:
    Verify the request's user access by mapping user's system wide roles found in JWT to local feature roles.
* Explicit:
    Verify if there is a role assignment for a given user and role. Explicit access is used when we manually want
    to give access to a user to a specific resource without creating any role data in JWT.

.. note::

    In both the implicit and explicit access, role data has a context that tells which resource(s)
    the requesting user can access

Implementation
--------------
To add RBAC implicit and explicit authorization checks, you need to follow the below steps. Here we are using ``LMS``,
`edx-enterprise-data <https://github.com/edx/edx-enterprise-data/>`_ and `ecommece <https://github.com/edx/ecommerce>`_
codebases as an example.  There is also an `RBAC demo repo <https://github.com/iloveagent57/edx_rbac_demo/>`_ that
demonstrates how to configure django-rules, set up feature roles/mappings, define rule predicates and permissions, and
make use of those in a DRF viewset.

1. `Configure Django <https://github.com/dfunckt/django-rules#configuring-django>`_ to use the ``rules`` package:

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'rules.apps.AutodiscoverRulesConfig',
    )
    # ...
    AUTHENTICATION_BACKENDS = (
        # ...
        'rules.permissions.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

2. In LMS create a `system wide role data migration <https://github.com/edx/edx-enterprise/blob/master/enterprise/migrations/0066_add_system_wide_enterprise_operator_role.py>`_. You only need to do this if you are creating a new role. We create
   system wide role when we want to give access to users to a system wide resource, for example, being a Course Instructor
   for a specific Course.

3. For implicit access, In LMS create a system wide role assignment for a user using django admin at
   ``/admin/enterprise/systemwideenterpriseuserroleassignment/``. LMS must have a ``SYSTEM_WIDE_ROLE_CLASSES`` django
   setting which contains the name of system wide role assignment model class. This will be used to add role data in JWT
   by LMS using ``create_role_auth_claim_for_user`` rbac util function. A ``SYSTEM_WIDE_ROLE_CLASSES`` django setting
   will look like below

.. code-block:: python

    SYSTEM_WIDE_ROLE_CLASSES = ['enterprise.SystemWideEnterpriseUserRoleAssignment']


Below is a sample role data for a user in JWT and a table that explains the role data.

.. code-block:: python

    "roles": [
        "enterprise_admin:e156c8d1-1bd8-e284-acfa-9008969023b0",
        "enterprise_openedx_operator:*"
    ]

+-----------------------+-----------------------+-----------------------+
| role name             | role context          | note                  |
+=======================+=======================+=======================+
| enterprise_admin      | e156c8d1-1bd8-e284-ac | user has access to a  |
|                       | fa-9008969023b0       | resource identified   |
|                       |                       | by                    |
|                       |                       | e156c8d1-1bd8-e284-ac |
|                       |                       | fa-9008969023b0       |
+-----------------------+-----------------------+-----------------------+
| enterprise_openedx_op | \*                    | user has access to    |
| erator                |                       | all resources         |
+-----------------------+-----------------------+-----------------------+


4. For explicit access, In an edx service like `edx-enterprise-data <https://github.com/edx/edx-enterprise-data/>`_
   create a feature specific wide role assignment for a user from within django admin
   at ``/admin/enterprise_data_roles/enterprisedataroleassignment/``


5. In a service create a system-to-feature roles mapping in django settings like below

.. code-block:: python

    ENTERPRISE_DATA_ADMIN_ROLE = 'enterprise_data_admin'
    SYSTEM_ENTERPRISE_ADMIN_ROLE = 'enterprise_admin'
    SYSTEM_ENTERPRISE_OPERATOR_ROLE = 'enterprise_openedx_operator'

    SYSTEM_TO_FEATURE_ROLE_MAPPING = {
        SYSTEM_ENTERPRISE_ADMIN_ROLE: [ENTERPRISE_DATA_ADMIN_ROLE],
        SYSTEM_ENTERPRISE_OPERATOR_ROLE: [ENTERPRISE_DATA_ADMIN_ROLE],
    }


6. Add rules for implicit and explicit authorization checks using below rbac util functions
    a. request_user_has_implicit_access_via_jwt
    b. user_has_access_via_database

    An actual implementation of rules can be seen in
    `rules.py <https://github.com/edx/edx-enterprise-data/blob/master/enterprise_data_roles/rules.py>`_ in
    edx-enterprise-data codebase. We use `django-rules <https://github.com/dfunckt/django-rules>`_ to
    do object-level permission checking. Check its `documentation <https://github.com/dfunckt/django-rules#using-rules>`_
    to get detailed information on how to create and use rules.


7. Add ``permission_required`` decorator on individual endpoints. All the positional arguments to decorator will be
treated as name of permissions we want to apply on endpoint and the second argument should be keyword argument named as
``fn`` and its value could be a callable or any python object. Callable signature should match
``(request, *args, **kwargs)``. Either the plain python object or value returned by the callable will
be passed to rules predicate as second parameter. Below is an endpoint with the decorator applied.

.. code-block:: python

    from edx_rbac.decorators import permission_required

    @detail_route()
    @permission_required('enterprise.can_view_catalog', fn=lambda request, pk: pk)
    def courses(self, request, pk=None):


8. Use ``PermissionRequiredMixin`` mixin for all endpoints in a viewset. A viewset must define a class level variable
named as ``permission_required`` and its value can be single permission name of list of permission names to be applied
on all endpoints in the viewset.
Below is a ViewSet with mixin.

.. code-block:: python

    from edx_rbac.mixins import PermissionRequiredMixin

    class EnterpriseViewSet(PermissionRequiredMixin, viewsets.ViewSet):
        authentication_classes = (JwtAuthentication,)
        pagination_class = DefaultPagination
        permission_required = 'can_access_enterprise'

9. Implement the ``self.get_permission_object`` method on a viewset in order to retrieve the permissions
object to check against. This object gets passed to the rule predicate(s). Without this method implemented,
the object passed to the rule predicate(s) will always be `None`. Note: django-rules does not support filtering
a queryset by a user's object-level permissions.

10. You are all setup and now when an endpoint gets a request, role based permissions will be checked for the requesting
user and either HTTP 403 or any other appropriate response will be returned. In case of HTTP 403, user have no access on
requesting resource.


Admin Interface
---------------
For explicit access, role assignment for a user is created through django admin, so you have to add/inherit appropriate
rbac model and form classes in your service. You can see an actual admin implementation `here <https://github.com/edx/edx-enterprise-data/blob/master/enterprise_data_roles/admin.py>`_
