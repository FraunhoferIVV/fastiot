.. _label-cli-intro:

###########################################################################
fiot CLI Introduction - Generating config files, building Docker containers
###########################################################################

.. contents::
   :local:

The ``fiot`` is your best tool for managing the build process of any FastIoT-project. It takes care of building docker
images using files stored in :file:`build`, generating configs from deployments under :file:`generated`, generating a :file:`generated.py` file for testing
purposes and manage local deployments. See :ref:`project_structure` for more information about the general structure of a FastIoT project.

Setting environment variables
=============================

If you need to adjust to a local environment with own docker registry, own Python Package Index (PyPi) please refer to
:ref:`tut-adapting_build_system`. Otherwise the defaults should be suitable for you to get started immediately.

Executing the command line interface (CLI)
==========================================

You can execute it like ``fiot <args>`` after installing FastIoT with pip. Call ``fiot -h`` for additional help.

*Hint:* When developing the framework itself this command is not available. You have to add the :file:`src` directory to
your :envvar:`PYTHONPATH` and and execute ``bin/fiot`` instead. Run the following from the FastIoT project root dir:

.. code-block:: bash

  export PYTHONPATH="$PWD/src":$PYTHONPATH
  bin/fiot --help

Docker Images and custom docker-compose files based on your sam-compose.yaml are built via ``fiot build`` and
``fiot config``, respectively. Before running your first project you always need to build the docker-compose
file, thus you need to run ``fiot config`` at least once.

To compile modules, add flag ``fiot build --mode=release``. Per default no modules will be compiled and will be
run with python interpreter.


Creating and executing your deployment configurations
=====================================================

A deployment usually consists of at least the message broker, probably some services you wrote your own or reused from
other people or projects and maybe a database or something similar.
Even for Testing you usually want to have at least a message broker.

In a freshly created project, you will have a deployment called "integration_test", which will provide these basics.
If you now run ``fiot config`` a docker-compose file will be created to start the services as docker containers.

To run the deployment simply use ``fiot start --use-test-deployment``. Now you have the message broker ready!

If you configured your project correctly in the last tutorial you should now be able to start the service locally and
have it communicate with the broker.



Building Docker Images
=======================

If you want to run your services continuously you can generate Docker containers using the framework easily, just run
``fiot build``.

This will create Dockerfiles in :file:`build/docker` for each service configured and build them.

Some additional notes
=====================

The generated files will be put into :file:`build/deployments/your_project`
Using this generated :file:`docker-compose.yaml` you can start modules and services like the nats broker or the database.

