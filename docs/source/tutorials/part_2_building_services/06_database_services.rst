.. _database_services:

Working with databases
======================

In FastIoT Framework there are several database helper functions for connecting a database.

But to reduce the FastIoT framework size, those libraries must be additionally installed.
Most of the times this can be done with a package option like ``fastiot[mongodb]``.

The full list of services already included for simple adding is at :mod:`fastiot.cli.common.infrastructure_services`.

MongoDB
-------

Add ``mongodb`` to your :file:`deployment.yaml` and also consult
:class:`fastiot.cli.common.infrastructure_services.MongoDBService` for more information about the service.

*Hint:* When working with a Raspberry Pi only MongoDB upto version 4 is working.
Please use :class:`fastiot.cli.common.infrastructure_services.MongoDB4Service` in this case!

The environment variables are documented at :class:`fastiot.env.env.MongoDBEnv`

For MongoDB you can use :func:`fastiot.db.mongodb_helper_fn.get_mongodb_client_from_env` to create a mongodb client.
After setting all relevant env variables you may access mongodb client through following code:

.. code:: python

  mongodb_client = get_mongodb_client_from_env()
  mongodb_client.insertOne({'my_var': 42})

With `mongodb_client` you can access all functions in mongodb api. Details s. https://pymongo.readthedocs.io/en/stable/index.html

MariaDB
-------

Add ``mariadb`` as service to your :file:`deployment.yaml` and see
:class:`fastiot.cli.common.infrastructure_services.MariaDBService` for adding e.g. an Entrypoint volume mount.

The environment variables are documented at :class:`fastiot.env.env.MariaDBEnv`

To access your database you may use :func:`fastiot.db.mariadb_helper_fn.get_mariadb_client_from_env` to create a mariadb client.

.. code:: python

  mariadb_client = get_mariadb_client_from_env()

`mariadb_client` includes all functions from mariadb api. Details s. https://mariadb-corporation.github.io/mariadb-connector-python/usage.html


InfluxDB
--------

Add ``influxdb`` to your :file:`deployment.yaml` and also consult
:class:`fastiot.cli.common.infrastructure_services.InfluxDBService` for more information about the service.

The environment variables are documented at :class:`fastiot.env.env.InfluxDBEnv`

For InfluxDB you can use :func:`fastiot.db.influxdb_helper_fn.get_async_influxdb_client_from_env` to create a influxdb client.

.. code:: python

  influxdb_client = await get_async_influxdb_client_from_env()

This function will return a async `influxdb_client`.
For more details see https://influxdb-client.readthedocs.io/en/stable/usage.html#how-to-use-asyncio


TimeScaleDB
-----------

Add ``timescaledb`` to your :file:`deployment.yaml` and also consult
:class:`fastiot.cli.common.infrastructure_services.TimeScaleDBService` for more information about the service.

The environment variables are documented at :class:`fastiot.env.env.TimeScaleDBEnv`

For TimeScaleDB you can use :func:`fastiot.db.time_scale_helper_fn.get_timescaledb_client_from_env` to create a time scale connection.

.. code:: python

  time_scale_db_client = get_timescaledb_client_from_env()

With this `time_scale_db_client` you can access all functions in psycopg2 api. Before working with psycopg2, the
`libpq-dev` must be manually installed in your OS to install the Python package `psycopg2`!
For details s. https://www.psycopg.org/docs/

