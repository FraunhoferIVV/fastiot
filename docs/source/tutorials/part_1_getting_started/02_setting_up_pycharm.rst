.. _label-setting-up-pycharm:

##################################
Setting up PyCharm for development
##################################

.. contents::
   :local:

Goal
====

After having checked out your project you want to get started and develop on existing modules. There you need to open your freshly created or checked out project in PyCharm.

First mark your ``src``-Directory as Sources Root: Right click on the directory in the Project view, nearly at the bottom select "Mark directory as" and select "Sources Root". The src directory should now appear in blue.
Next some more things need to be working in order for your module to start:

* A working Docker-Environment
* Generation of docker-compose files using the CLI.
* Active Environment Variables

Docker
======

**Attention:**
 You need to be in the docker-Group on your Linux system to be allowed to start docker containers and the docker service needs to be running.

 To check you can run ``docker container ls`` to see any potentially running docker containers or you will receive a, hopefully, helpful error message.

You may use the commandline to work with the file generated in :file:`build/deployments/*/docker-compose.yaml`

More intuitive for beginners is the use of the PyCharm Docker-Plugin:
 1. Install in PyCharm with File -> Settings -> Plugins
 2. Search for Docker and install the plugin
 3. After restarting PyCharm you can start single docker containers as well as the complete project with all containers from the GUI. Just open the corresponding docker-compose.yaml file.


Environment Variables
=====================

A lot of services within docker depend on a proper setup of environment variables just as some helpers and clients within the framework.
To bring data into Docker containers this is, next to configuration files mounted into the volume, one of the classical methods.

It is possible to define all environment variables in a .env-file. This is recommended as PyCharm can read this file:
 1. Install in PyCharm with File -> Settings -> Plugins
 2. Search for EnvFile (Plugin by Borys Pierov) in the market place and install the plugin. If the plugin does not show up you may have to restart PyCharm and try again.
 3. Restart Pycharm or the plugin menu wont appear in the next step


Starting your services
======================

Now it’s time to make your module ready for the first start:

 1. Right Click on the run.py of your service
 2. Below Run and Debug there is a Python Symbol with "Create 'run'…", click it
 3. In the Tab "EvnFile" activate "Enable EnvFile" and on the right select the + and add your .env-File from :file:`build/deployments/your_project/.env`
     *Hint:* You may need to make hidden files visible using the Eye-Icon in the selection field
     *Hint:*  Instead of using your own deployment you can also refer to the already created deployment "integration_test", which should provide sufficient defaults.
 4. Also add the :file:`local-testing-overwrite.env` just as in the previous step if found within the deployment.
     *Explanation:* The default is to access e.g. the nats broker by the hostname ``nats`` within the docker-compose environment. To actually access the broker running on your machine you need to overwrite this with localhost, which is done using this file.
 5. Change the working directory to the root of your project, so remove everything in the field starting at :file:`src` (:file:`src` *must not* be in the line any more).
 6. You may provide a Name for the configuration, e.g. MyModule to differentiate between various run-Configs for all of your modules
 7. Click OK

Technically your service is now able to start. But you usually will need at least a message broker to be running for
everything to start up. Please refer to the next tutorial at :ref:`label-cli-intro` about how to create proper
configurations to get the infrastructure services started.
