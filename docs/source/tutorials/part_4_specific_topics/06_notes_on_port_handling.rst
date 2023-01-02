====================================
Some notes on working with TCP ports
====================================

Working on many projects (or with many people on the same terminal server) can easily cause trouble when everyone tries
to use the same ports for a service.
As an example, the message broker nats runs on TCP-port 4222 per default. This works well when using only one broker on
the machine but will cause severe trouble when running the service multiple times for different projects.

Therefore a complex logic has been integrated in the configuration handling and creation of docker-compose files.


Automatic port selection
------------------------

Use the command ``fiot config --port-offset=0`` to use random ports free at the moment of creating the config file for
the first time.

**Hint:** You may also use the :envvar:`FASTIOT_PORT_OFFSET` to set a system-wide default.

After starting the integration test deployment unit tests will use the freshly set ports right away.
If you configured your project as proposed in :ref:`label-setting-up-pycharm` this will also use these ports as those
are now stored in the deplomynet-specific directory below :file:`build/deployments`.

**Attention:** Because some local tools e.g. a database client might be configured with ports; it's not feasable to have
new random ports each time you run ``fiot config``. That's why the config cmd will try to import generated ports from
the built configuration. If you don't want this behavior, you can use the no-use-port-import option like this:
``fiot config --port-offset=0 --no-use-port-import``.
This will generate completely new ports, unless your :file:`.env` in your :file:`deployments/my_deployment/` has
something statically configured.

**Attention**: Even though there are 65336 ports (0..1024 only available to users with system privileges) it may happen,
that a port is in use when you start your deployment. In this case you have to rerun fiot config with the option
``-no-use-port-import``. If this happens often you might assign ports with specified ranges e.g. --port-offset=6000 and
have a different offset for each project and user.


Manual port selection
---------------------

If you use any environment variables in your :file:`.env` file inside your deployment configuration
you can simply fixate ports there, e.g.:

::

  FASTIOT_MONGO_DB_PORT=20334

will set the TCP port for a MongoDB to ``20334``.
See :ref:`deployment_yaml` for more details on handling deployments).


Ports within the docker networks
--------------------------------

Using the generated :file:`.env` file in the build directory, you will see the hostnames of e.g. the broker set to
``localhost``. This works well for debugging or running services locally.
But inside the Docker-network these services need to be addressed with their internal port and hostname (typically the
container name. To solve this issue, the env variables will be overwritten inside the :file:`docker_compose.yaml`
accordingly. Thus ``localhost:12345`` to access the broker on port 12345 will become ``nats:4222`` inside a running
docker container.

The framework will take care of creating correct :file:`docker-compose.yaml` files. So just be aware of these small
differences!
