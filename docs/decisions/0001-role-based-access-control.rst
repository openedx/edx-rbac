1. Role Based Access Control
----------------------------

Status
------

Accepted


Context
-------
In the OpenedX system, we have the concept of different types of users, or roles, such as an Enterprise Learner or a
Course Administrator. These roles potentially impact behavior across the OpenedX system, and features increasingly
depend on being aware of this information for a user. Additionally, the types of users that are important in an OpenedX
system may be different from instance to instance. As we embark on adding features, we need a way to assign users to
these different roles and to have different services within the OpenedX ecosystem enforce permissions related to these
roles. We also need the ability to create new roles that map to different sets of permissions as product needs arise.


Decision
--------
The underlying engineering problem that the OpenedX system faces is the lack of a system that provides robust
authorization capabilities. Based on our requirements, it made sense to proceed with implementing authorization
checks using Role Based Access Control (RBAC), where users can be granted one or more roles which are each mapped
to a set of permissions. Using RBAC we can control access for a user at different levels of granularity.
To support RBAC in the OpenedX ecosystem, this repository was created to provide standardized ways of defining
roles and permission mappings and performing permission checks in any django application that requires RBAC.


Consequences
------------
As a result of these changes, any django application within the OpenedX system can extend this functionality to
implement their own RBAC permissions with little overhead. Also, if any new functionality is needed related to RBAC,
it should be part of this repo so that the functionality is available to all features that may need it

References
----------


