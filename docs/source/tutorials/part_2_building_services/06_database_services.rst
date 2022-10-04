.. _database_services:

===========================
Database Services
===========================
In FastIoT Framework there are several database helper functions for connecting a database.
But to reduce the FastIoT framework size, those libraries must be additionally installed.

- For **MongoDB**: you can use :func:`fastiot.db.mongodb_helper_fn.get_mongodb_client_from_env` to create a mongodb client.
After setting all relevant env variables (s. :func:`fastiot.db.mongodb_helper_fn.get_mongodb_client_from_env`), you can access mongodb client through following code:

.. code:: python

  client_wrapper = get_mongodb_client_from_env()
  client_wrapper.client.insertOne()

With `client_wrapper.client` you can access all functions in mongodb api. Details s. https://pymongo.readthedocs.io/en/stable/index.html

- For **MariaDB**: you can use :func:`fastiot.db.mariadb_helper_fn.open_mariadb_connection_from_env` to create a mariadb connection.

.. code:: python

  mariadb_connection = open_mariadb_connection_from_env()

`mariadb_connection` includes all functions from mariadb api. Details s. https://mariadb-corporation.github.io/mariadb-connector-python/usage.html

- For **InfluxDB**: you can use :func:`fastiot.db.influxdb_helper_fn.get_async_influxdb_client_from_env` to create a influxdb client.

.. code:: python

  influxdb_client = await get_async_influxdb_client_from_env()

This function will return a async `influxdb_client`. Details s. https://influxdb-client.readthedocs.io/en/stable/usage.html#how-to-use-asyncio

- For **TimeScaleDB**: you can use :func:`fastiot.db.time_scale_helper_fn.open_timescaledb_connection_from_env` to create a time scale connection.

.. code:: python

  db_connection = open_timescaledb_connection_from_env()

With this `db_connection` you can access all functions in psycopg2 api. Before working with psycopg2, the libpq-dev must be manuelly installed in your OS to install psycopg2 !
Details s. https://www.psycopg.org/docs/

