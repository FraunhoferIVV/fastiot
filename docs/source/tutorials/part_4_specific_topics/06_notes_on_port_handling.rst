====================================
Some notes on working with TCP ports
====================================

Working on many projects (or with many people on the same terminal server) can easily cause trouble when everyone tries
to use the same ports for a service.
The message broker nats e.g. uses TCP-port 4222 as default.
This works well when using only one broker on the machine but will cause sever trouble when trying to start the
service multiple times.

Therefore a complex logic has been integrated in the configuration handling and creation of docker-compose files.

Automatic port selection
------------------------

Use the command ``fiot config --port-offset=0`` to use random ports free at the moment of creating the config file.

**Hint:** You may also use the :envvar:`FASTIOT_PORT_OFFSET` to set a system-wide default.

After starting the integration test deployment unit tests will use the freshly set ports right away.
If you configured your project as proposed in :ref:`label-setting-up-pycharm` this will also use these ports.

**Attention**: Even thought there are 65336 ports (0..1024 only available to users with system privileges) it may happen,
that a port is in use when you start your deployment again.
Rerunning the config command to assign a different port will help!

When running ``fiot config --port-offset=0`` your :file:`docker-compose.yaml` will have different ports.
Especially when running a database you will have to reconfigure the port everytime after running the config command.
This is where you may want to use a more manual way to keep at least some ports static.


Manual port selection
---------------------

If you use any environment variables in your :file:`.env` file inside your deployment configuration
you can simply fixate ports there:

::

  FASTIOT_MONGO_DB_PORT=20334

will set the TCP port for a MongoDB to ``20334``.
See :ref:`deployment_yaml` for more details on handling deployments).


Ports within the docker networks
--------------------------------

Using the generated :file:`.env` file in the build directory you will see the hostnames of e.g. the broker set to
``localhost``. This works well for debugging.
But inside the Docker-network the services need to be addressed with their internal port and hostname (typically the
container name.
Thus ``localhost:12345`` to access the broker on port 12345 will become ``nats:4222``. The framework will
take care of creating correct :file:`docker-compose.yaml` files.
So just be aware of these small differences!
