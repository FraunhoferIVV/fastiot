.. _label-setting-up-pycharm:

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

 To check you can run ``docker container ls`` to see any potentially running docker containers or you will receive a,
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

It is possible to define all environment variables in a .env-file. This is recommended as PyCharm can read this file:

1. Install in PyCharm with File -> Settings -> Plugins
2. Search for EnvFile (Plugin by Borys Pierov) in the market place and install the plugin. If the plugin does not show
   up you may have to restart PyCharm and try again.
3. Restart Pycharm or the plugin menu wont appear in the next step


Starting your services
----------------------

Now it’s time to make your module ready for the first start:

1. Right Click on the :file:`run.py` of your service
2. Below Run and Debug there is a Python Symbol with "Create 'run'…", click it
3. In the Tab "EnvFile" activate "Enable EnvFile" and on the right select the + and add your .env-File from
   :file:`build/deployments/integration_test/.env`

   *Hint:* You may need to make hidden files visible using the Eye-Icon in the selection field

   *Hint:* Instead of using the deployment 'integration_test` you can also refer to your own deployment.

   *Hint:* Please make sure to add the env-File from build dir because the generated .env file will also append
   defaults for hosts and ports to services which are missing in the original .env file.
4. Change the working directory to the root of your project, so remove everything in the field starting at :file:`src`
   (:file:`src` *must not* be in the line any more).
5. Optional: You may provide a Name for the configuration, e.g. MyModule to differentiate between various run-Configs
   for all of your modules
6. Click OK

Technically your service is now able to start.
You usually will need at least a message broker to be running for.
You may start the deployment with the command :command:`fiot start integration_test`.

Now you should really be able to start your service in Run or Debug-Mode.

Please refer to the next tutorial at :ref:`label-cli-intro` about how to create proper configurations to get the
infrastructure services started.
