Getting Started
===============

`uv`_ manages the development environment. ``make requirements`` creates a ``.venv`` directory in the
repository and installs the dependencies there; activate it with ``source .venv/bin/activate``. Unless
otherwise stated, assume all terminal code below is executed within that environment.

.. _uv: https://docs.astral.sh/uv/getting-started/installation/

Using Inside a Devstack Container
---------------------------------

You can develop and test edx-rbac inside a devstack docker container, as long as the repo
lives in your ``$DEVSTACK_WORKSPACE/src`` directory (which means it will be mounted into any container
running from devstack).  ``make requirements`` creates the environment in ``.venv/`` inside the repo -
this directory is git-ignored, but still "persists" between your host and any running devstack container.

.. code-block:: bash

    $ make app-shell # or however you get into your container's shell
    $ cd /edx/src/edx-rbac
    $ pip install uv # if uv isn't already installed in the container
    $ make requirements
    $ source .venv/bin/activate
    $ make test


Install dependencies
--------------------
Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements
