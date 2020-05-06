Getting Started
===============

If you have not already done so, create or activate a `virtualenv`_. Unless otherwise stated, assume all terminal code
below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/

Using Inside a Devstack Container
---------------------------------

You can develop and test edx-rbac inside a devstack docker container, as long as the repo
lives in your ``$DEVSTACK_WORKSPACE/src`` directory (which means it will be mounted into any container
running from devstack).  In the code snippet below, a python virtualenv for edx-rbac is created inside
a subdirectory called ``venvs/`` - this subdirectory is git-ignored, but still "persists" between
your host and any running devstack container.

.. code-block:: bash

    $ make app-shell # or however you get into your container's shell
    $ cd /edx/src/edx-rbac
    $ virtualenv venvs/edx-rbac # make a separate venv just for this library
    $ source venvs/edx-rbac/bin/activate
    $ make requirements
    $ make test


Install dependencies
--------------------
Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements
