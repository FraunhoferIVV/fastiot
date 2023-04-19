.. _label-setting-up-pycharm:

.. role:: python(code)
   :language: python

Setting up PyCharm for development
##################################

.. contents::
   :local:

Goal
----

After having checked out your project you want to get started and develop on new or existing modules.
There you need to open your freshly created or checked out project in PyCharm.

First mark your :file:`src`-Directory as Sources Root: Right click on the directory in the Project view, nearly at the
bottom select "Mark directory as" and select "Sources Root".
The directory :file:`src` should now appear in blue.
Next some more things need to be working in order for your module to start:

* A working Docker-Environment
* Generation of docker-compose files using the CLI.
* Active Environment Variables

Docker
------

**Attention:**
 You need to be in the docker-Group on your Linux system to be allowed to start docker containers and the docker
 service needs to be running.

 To check you can run :command:`docker container ls` to see any potentially running docker containers or you will receive a,
 hopefully, helpful error message.

You may use the commandline to work with the file generated in :file:`build/deployments/*/docker-compose.yaml` or use
the fastiot CLI.

For testing most of the time the integration test deployment is very suitable.

Environment Variables
---------------------

A lot of services within docker depend on a proper setup of environment variables just as some helpers and clients
within the framework.
To bring data into Docker containers this is, next to configuration files mounted into the volume, one of the classical
methods.

It is possible to define all environment variables in a .env-file.
The :file:`.env` from your :file:`build/integration_test`  will be read in automatically when you start the service
locally.
To change this to another deployment set the environment variable :envvar:`FASTIOT_USE_DEPLOYMENT` to the corresponding
deployment.


Starting your services
----------------------

First start your integration test deployment with the command :command:`fiot start integration_test`.
Now you should really be able to start your service in Run or Debug-Mode using either the :file:`run.py` in your service
or, if the service provides a :python:`if __name__ == '__main__'` you may also start your service directly.

Please refer to the next tutorial at :ref:`label-cli-intro` about how to create proper configurations to get the
infrastructure services started.
