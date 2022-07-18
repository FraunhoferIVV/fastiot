"""
Minimal module to read out nats messages
========================================

This module is intended for debugging purposes and not for longer production runs.

Per default this module tries to read out and print all data recursively under ``v1.``. You may adjust this and also add
some filters using environment variables defined in :class:`fastiot_core_services.nats_logger.env.NatsLoggerConstants`.


If not using a docker-compose file generated with your project you also have to set variables for broker and port
:envvar:`FASTIOT_NATS_HOST` and :envvar:`FASTIOT_NATS_PORT`.

For debugging you may run the container solo using the docker command like this

::

    docker run -e FASTIOT_NATS_BROKER_HOST="10.62.12.25" -e FASTIOT_NATS_BROKER_PORT="4222" \\
      -e FASTIOT_NATS_LOGGER_SUBJECT="v1.thing.my_sensor" \\
      -e FASTIOT_NATS_LOGGER_FILTER_FIELD="value" \\
      -e FASTIOT_NATS_LOGGER_FILTER_VALUE="5" \\
      docker.dev.ivv-dd.fhg.de/fastiot/nats_logger

If you want to run the container locally and connect to your local nats container you have to specify the network
manually.

#. First list your local docker networks with ``docker network ls``
#. Start docker with ``docker run --network your_local_FASTIOT-net -e FASTIOT_NATS_BROKER_HOST="nats"  …``
"""
