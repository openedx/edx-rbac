2. Adding a field to UserRoleAssignment that explicitly indicates wildcard assignment
-------------------------------------------------------------------------------------

Status
------

Accepted (January 2021)


Context
-------
It will be beneficial to explicitly capture the fact that some user-role assignments
are meant to apply to any (or all) contexts.  Capturing this as a model field,
rather than making an implicit determination based on, for example, the name of the role,
is easier to understand and should lead to better consistency in subclasses of the
``UserRoleAssignment`` model.

Decision
--------
We will add a boolean ``applies_to_all`` field to ``UserRoleAssignment``.  This field represents a "wildcard";
if true, it indicates that the instance's user has the role assigned for any and all contexts.
It will default to ``false``.

Consequences
------------
At the time of this writing, we're only adding the field to the model.  Modifications of logic
will happen in a subsequent version(s).
