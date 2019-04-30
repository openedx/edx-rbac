Change Log
----------

..
   All enhancements and patches to edx_rbac will be documented
   in this file.  It adheres to the structure of http://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (http://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

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
