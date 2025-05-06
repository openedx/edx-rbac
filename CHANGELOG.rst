Change Log
----------

..
   All enhancements and patches to edx_rbac will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
--------------------
[2.1.0]
--------
* Add Support for Djanog5.2

[2.0.0]
* Drop support for Python 3.8

[1.10.0]
--------
* Optionally ignore and log ``jwt.exceptions.InvalidTokenErrors`` when decoding JWT from cookie.

[1.9.0]
-------
* Add support for Python 3.11 & 3.12

[1.8.0]
-------
* Switch from ``edx-sphinx-theme`` to ``sphinx-book-theme`` since the former is
  deprecated
* Added support for Django 4.2

[1.7.0]
-------

* fix: ``utils.get_role_auth_claim_for_user()`` now preserves the order of (role, context) pairs
  as returned by the `get_assignment()` function.

[1.6.0] - 2022-01-19
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Drop support for Django<3.2
* Replacing ugettext with gettext to resolve RemovedInDjango40 error.
* Added Django40 Support

[1.5.1] - 2021-11-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Replacing ugettext_lazy with gettext_lazy to resolve RemovedInDjango40Warning.

[1.5.0] - 2021-07-07
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Added support for django 3.0, 3.1, 3.2

[1.4.2] - 2021-03-22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Modifies ``create_role_auth_claim_for_user`` to return a list of *unique*
  (role:context) entries, so that the JWT does not become too large
  to fit in cookies/headers.

[1.4.1] - 2021-01-22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Add a ``UserRoleAssignment.applies_to_all`` field, because explicit is better than implicit.
  See the ADR at `docs/decisions/0002-explicit-role-assignment-wildcard.rst`.

[1.4.0]
-------

* Update PyPI token.

[1.3.3] - 2020-10-02
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Removed ``python_2_unicode_compatible`` decorator.

[1.3.2] - 2020-07-28
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``PermissionRequiredForListingMixin.get_queryset()`` should allow falsey ``base_queryset`` properties, like
  an empty ``QuerySet`` object.  Adds tests to verify that this is the case.

[1.3.1] - 2020-06-16
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Update ``get_assignments()`` to guard against AnonymousUsers.
* Update ``contexts_accessible_from_database()`` to use ``get_assignments()`` instead of building a "custom" QuerySet.

[1.3.0] - 2020-06-11
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adds a PermissionRequiredForListingMixin that can be used in DRF ModelViewSets and supports a list action.
  This should allow list actions to return all of the elements from a base_queryset that
  the requesting user has access to, either via their JWT or DB-assigned roles.
* Adds/modifies utility functions that deal with permission-checking to support multiple roles and multiple contexts.

[1.2.1] - 2020-05-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Exposes a new ``utils.feature_roles_from_jwt()`` function, which, given a decoded JWT,
  will provide a mapping of feature roles to contexts/identifiers.
* Modifies ``utils.user_has_access_via_database()`` to check for multiple database role assignments
  for a given user and role name (i.e. uses a ``filter()`` instead of a ``get()``).

[1.2.0] - 2020-04-30
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Removed support for django 2.0 and 2.1
* Added Support for Python 3.8

[1.1.3] - 2020-04-13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Added check for AnonymousUser in user_has_access_via_database to prevent 500 errors.

[1.1.2] - 2020-03-27
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Added support for Django 2.0, 2.1, and 2.2.

[1.1.1] - 2020-03-02
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Fix bug in implicit role check when the same role has multiple contexts available.

[1.1.0] - 2020-02-18
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Update `PermissionRequiredMixin` to pass through an object to rule predicates, if `self.get_permision_required` exists and is callable


[1.0.5] - 2019-12-18
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Updated requirements.

[1.0.4] - 2019-12-17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Updated utils for user with multiple contexts.

[1.0.3] - 2019-09-12
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Use functools.wraps to prevent the decorator from swallowing the view name

[1.0.2] - 2019-07-12
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* store current request on thread local storage using crum.

[1.0.1] - 2019-05-27
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* edx-drf-extensions version upgrade.

[1.0.0] - 2019-05-20
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Removed `get_request_or_stub` and `get_decoded_jwt_from_request` from utils.py

[0.2.1] - 2019-05-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* edx-drf-extensions version upgrade.

[0.2.0] - 2019-04-30
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Check for JWT presence in implicit permission.
* Refactor role retrieval to remove the dependency on django models for assigning roles.

[0.1.11] - 2019-04-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Get JWT token from request.auth if it is not set on the cookie. This supports client credentials oauth2 flow.

[0.1.10] - 2019-04-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Update context checks for implicit and explicit access for all resources access.

[0.1.9] - 2019-04-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adding support for checking context for implicit and explicit access.

[0.1.8] - 2019-03-22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adding an additional argument for the permission_required decorator

[0.1.7] - 2019-03-20
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adding a mixin for authz permissions support.

[0.1.6] - 2019-03-19
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adding a decorator for authz permissions support.

[0.1.5] - 2019-03-18
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adding django admin support for models extending UserRoleAssignment.

[0.1.4] - 2019-03-07
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adding a number of utils for roles in JWTs and the database

[0.1.3] - 2019-03-07
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Adding get_context to the UserRoleAssignment class.

[0.1.2] - 2019-03-06
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Quality fixes

[0.1.1] - 2019-03-06
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Bumping version so we get pip updated with new models we added

[0.1.0] - 2019-02-28
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
