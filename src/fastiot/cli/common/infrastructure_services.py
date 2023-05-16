"""
Infrastructure Services
=======================

This file contains all preconfigured infrastructure services.
Those are easy to integrate just by adding their name into the ``infrastructure-services:`` key in your
:file:`deployment.yaml`.
"""

from typing import List

from fastiot.cli.model.infrastructure_service import InfrastructureService, InfrastructureServicePort, \
    InfrastructureServiceEnvVar, InfrastructureServiceVolume, InfrastructureServiceComposeExtras
from fastiot.env.env_constants_basic import FASTIOT_NATS_HOST, FASTIOT_NATS_PORT
from fastiot.env.env_constants_db import FASTIOT_TIME_SCALE_DB_VOLUME, FASTIOT_REDIS_VOLUME, FASTIOT_MONGO_DB_VOLUME, \
    FASTIOT_MARIA_DB_VOLUME, FASTIOT_MARIA_DB_ENTRY, FASTIOT_INFLUX_DB_MODE, FASTIOT_INFLUX_DB_VOLUME, \
    FASTIOT_ELASTICSEARCH_HOST, FASTIOT_ELASTICSEARCH_PORT, FASTIOT_ELASTICSEARCH_PASSWORD, \
    FASTIOT_ELASTICSEARCH_VOLUME, FASTIOT_TIME_SCALE_DB_HOST, FASTIOT_TIME_SCALE_DB_PORT, FASTIOT_TIME_SCALE_DB_USER, \
    FASTIOT_TIME_SCALE_DB_PASSWORD, FASTIOT_TIME_SCALE_DB_DATABASE, FASTIOT_REDIS_HOST, FASTIOT_REDIS_PORT, \
    FASTIOT_REDIS_PASSWORD, FASTIOT_MONGO_DB_HOST, FASTIOT_MONGO_DB_PORT, FASTIOT_MONGO_DB_USER, \
    FASTIOT_MONGO_DB_PASSWORD, FASTIOT_MONGO_DB_MEM_LIMIT, FASTIOT_MARIA_DB_HOST, FASTIOT_MARIA_DB_PORT, \
    FASTIOT_MARIA_DB_USER, FASTIOT_MARIA_DB_PASSWORD, FASTIOT_INFLUX_DB_HOST, FASTIOT_INFLUX_DB_PORT, \
    FASTIOT_INFLUX_DB_USER, FASTIOT_INFLUX_DB_PASSWORD, FASTIOT_INFLUX_DB_ORG, FASTIOT_INFLUX_DB_BUCKET, \
    FASTIOT_INFLUX_DB_TOKEN


class NatsService(InfrastructureService):
    """
    Service definition for the nats message broker.

    Usually no configuration is needed for this service!
    """

    name: str = 'nats'
    image: str = 'nats:latest'
    host_name_env_var = FASTIOT_NATS_HOST
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=4222,
            default_port_mount=4222,
            env_var=FASTIOT_NATS_PORT
        )
    ]


class MariaDBService(InfrastructureService):
    """
    Definition of the Service to use `MariaDB <https://mariadb.com>`_.

    The environment variables are documented at :class:`fastiot.env.env.MariaDBEnv`.

    With the following steps you are able to provision your MariaDB with an initial SQL-File at the first start:
      1. Add a file like :file:`entry.sql` to your deployment dir
      2. Add the environment variable :envvar:`FASTIOT_MARIA_DB_ENTRY` to your :file:`.env` in the deployment dir like
         ``FASTIOT_MARIA_DB_ENTRY='./entry.sql'``
      3. Run :command:`fiot config` to update your configuration.

    .. seealso::
       :ref:`database_services`
           How to add databases to your service.
    """
    name: str = 'mariadb'
    image: str = 'mariadb:10.8'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=3306,
            default_port_mount=3306,
            env_var=FASTIOT_MARIA_DB_PORT
        )
    ]
    environment: List[InfrastructureServiceEnvVar] = [
        InfrastructureServiceEnvVar(
            name='MYSQL_ROOT_USER',
            default='root',
            env_var=FASTIOT_MARIA_DB_USER
        ),
        InfrastructureServiceEnvVar(
            name='MYSQL_ROOT_PASSWORD',
            default='12345',
            env_var=FASTIOT_MARIA_DB_PASSWORD
        ),
        # Causes timezone information import to be skipped as this seems to take quite some time as of 10/2019 and
        # MariaDB 10.4
        # Check if this can be removed at a later point
        InfrastructureServiceEnvVar(
            name='MYSQL_INITDB_SKIP_TZINFO',
            default='yes'
        )
    ]
    host_name_env_var = FASTIOT_MARIA_DB_HOST
    password_env_vars: List[str] = ["FASTIOT_MARIA_DB_PASSWORD"]
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/var/lib/mysql',
            env_var=FASTIOT_MARIA_DB_VOLUME
        ),
        InfrastructureServiceVolume(
            container_volume='/docker-entrypoint-initdb.d/entry.sql',
            default_volume_mount='',
            env_var=FASTIOT_MARIA_DB_ENTRY,
            tmpfs_for_tests=False  # mounting literally nothing to an entry point does not make sense => Don’t use tmpfs
        )
    ]


class MongoDBService(InfrastructureService):
    """
    Definition of the service to use a MongoDB.

    .. seealso::
       :ref:`database_services`
           How to add databases to your service.
    """
    name: str = 'mongodb'
    image: str = 'mongo:5.0'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=27017,
            default_port_mount=27017,
            env_var=FASTIOT_MONGO_DB_PORT
        )
    ]
    environment: List[InfrastructureServiceEnvVar] = [
        InfrastructureServiceEnvVar(
            name='MONGO_INITDB_ROOT_USERNAME',
            default='root',
            env_var=FASTIOT_MONGO_DB_USER
        ),
        InfrastructureServiceEnvVar(
            name='MONGO_INITDB_ROOT_PASSWORD',
            default='12345',
            env_var=FASTIOT_MONGO_DB_PASSWORD
        )
    ]
    host_name_env_var = FASTIOT_MONGO_DB_HOST
    password_env_vars: List[str] = [FASTIOT_MONGO_DB_PASSWORD]
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/data/db',
            env_var=FASTIOT_MONGO_DB_VOLUME
        )
    ]
    compose_extras: List[InfrastructureServiceComposeExtras] = [
        InfrastructureServiceComposeExtras(
            option_name='mem_limit',
            env_var=FASTIOT_MONGO_DB_MEM_LIMIT
        )
    ]


class MongoDB4Service(MongoDBService):
    """
    Infrastructure service for a MongoDB in version 4.

    This is the latest version to work with a Raspberry Pi 4
    (s. https://stackoverflow.com/questions/68419196 for more details)
    """
    name: str = 'mongodb4'
    image: str = 'mongo:4.4.18'


class InfluxDBService(InfrastructureService):
    """
    Definition of the InfluxDB Service

    .. seealso::
       :ref:`database_services`
           How to add databases to your service.
    """
    name: str = 'influxdb'
    image: str = 'influxdb:2.0'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=8086,
            default_port_mount=8086,
            env_var=FASTIOT_INFLUX_DB_PORT
        )
    ]
    environment: List[InfrastructureServiceEnvVar] = [
        InfrastructureServiceEnvVar(
            name='DOCKER_INFLUXDB_INIT_USERNAME',
            default='influx_db_admin',
            env_var=FASTIOT_INFLUX_DB_USER
        ),
        InfrastructureServiceEnvVar(
            name='DOCKER_INFLUXDB_INIT_PASSWORD',
            default='mf9ZXfeLKuaL3HL7w',
            env_var=FASTIOT_INFLUX_DB_PASSWORD
        ),
        InfrastructureServiceEnvVar(
            name='DOCKER_INFLUXDB_INIT_MODE',
            default='setup',
            env_var=FASTIOT_INFLUX_DB_MODE
        ),
        InfrastructureServiceEnvVar(
            name='DOCKER_INFLUXDB_INIT_ORG',
            default='FASTIOT',
            env_var=FASTIOT_INFLUX_DB_ORG
        ),

        InfrastructureServiceEnvVar(
            name='DOCKER_INFLUXDB_INIT_BUCKET',
            default='things',
            env_var=FASTIOT_INFLUX_DB_BUCKET
        ),
        InfrastructureServiceEnvVar(
            name='DOCKER_INFLUXDB_INIT_ADMIN_TOKEN',
            default='12345',
            env_var=FASTIOT_INFLUX_DB_TOKEN
        )
    ]
    host_name_env_var = FASTIOT_INFLUX_DB_HOST
    password_env_vars: List[str] = [FASTIOT_INFLUX_DB_TOKEN, FASTIOT_INFLUX_DB_PASSWORD]
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/var/lib/influxdb2',
            env_var=FASTIOT_INFLUX_DB_VOLUME
        )
    ]


class TimeScaleDBService(InfrastructureService):
    """
    Definition of a TimeScaleDB Service

    .. seealso::
       :ref:`database_services`
           How to add databases to your service.
    """
    name: str = 'timescaledb'
    image: str = 'timescale/timescaledb:latest-pg14'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=5432,
            default_port_mount=5432,
            env_var=FASTIOT_TIME_SCALE_DB_PORT
        )
    ]
    environment: List[InfrastructureServiceEnvVar] = [
        InfrastructureServiceEnvVar(
            name='POSTGRES_USER',
            default='postgres',
            env_var=FASTIOT_TIME_SCALE_DB_USER
        ),
        InfrastructureServiceEnvVar(
            name='POSTGRES_PASSWORD',
            default='12345',
            env_var=FASTIOT_TIME_SCALE_DB_PASSWORD
        ),
        InfrastructureServiceEnvVar(
            name='POSTGRES_DB',
            default='fastiot_db',
            env_var=FASTIOT_TIME_SCALE_DB_DATABASE
        ),
    ]
    host_name_env_var: str = FASTIOT_TIME_SCALE_DB_HOST
    password_env_vars: List[str] = [FASTIOT_TIME_SCALE_DB_PASSWORD]
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/var/lib/postgresql/data',
            env_var=FASTIOT_TIME_SCALE_DB_VOLUME
        )
    ]


class RedisService(InfrastructureService):
    """
    Definition of the Redis Service.

    .. seealso::
       :class:`fastiot.db.redis_helper.RedisHelper`
          How to easily interact using the integrated RedisHelper.
       :mod:`fastiot_sample_services.redis_producer`
          Example service for sending and receiving data over a Redis Server.
    """
    name: str = 'redis'
    image: str = 'redis:7'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=6379,
            default_port_mount=6379,
            env_var=FASTIOT_REDIS_PORT
        )
    ]
    environment: List[InfrastructureServiceEnvVar] = [
        InfrastructureServiceEnvVar(
            name='REDIS_PASSWORD',
            default='12345',
            env_var=FASTIOT_REDIS_PASSWORD
        )
    ]

    host_name_env_var = FASTIOT_REDIS_HOST
    password_env_vars: List[str] = [FASTIOT_REDIS_PASSWORD]
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/data',
            env_var=FASTIOT_REDIS_VOLUME
        )
    ]


