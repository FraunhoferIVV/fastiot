from typing import List

from fastiot.cli.model.infrastructure_service import InfrastructureService, InfrastructureServicePort, \
    InfrastructureServiceEnvVar, InfrastructureServiceVolume
from fastiot.env import FASTIOT_NATS_PORT, FASTIOT_MARIA_DB_PORT, FASTIOT_MONGO_DB_PORT, FASTIOT_MONGO_DB_USER, \
    FASTIOT_MONGO_DB_PASSWORD, FASTIOT_MARIA_DB_PASSWORD, FASTIOT_MONGO_DB_VOLUME, FASTIOT_MARIA_DB_VOLUME, \
    FASTIOT_MARIA_DB_HOST, FASTIOT_MONGO_DB_HOST, FASTIOT_NATS_HOST, FASTIOT_INFLUX_DB_PORT, FASTIOT_INFLUX_DB_TOKEN, \
    FASTIOT_INFLUX_DB_HOST, FASTIOT_INFLUX_DB_VOLUME, FASTIOT_INFLUX_DB_MODE, FASTIOT_INFLUX_DB_BUCKET, \
    FASTIOT_INFLUX_DB_USER, FASTIOT_INFLUX_DB_PASSWORD, FASTIOT_INFLUX_DB_ORG, FASTIOT_TIME_SCALE_DB_PORT, \
    FASTIOT_TIME_SCALE_DB_USER, FASTIOT_TIME_SCALE_DB_PASSWORD, FASTIOT_TIME_SCALE_DB_DATABASE, \
    FASTIOT_TIME_SCALE_DB_HOST, FASTIOT_TIME_SCALE_DB_VOLUME, FASTIOT_MARIA_DB_USER, FASTIOT_REDIS_PORT, \
    FASTIOT_REDIS_HOST, FASTIOT_REDIS_PASSWORD, FASTIOT_REDIS_VOLUME
from fastiot.env.env_constants import FASTIOT_ELASTICSEARCH_HOST, FASTIOT_ELASTICSEARCH_PASSWORD, FASTIOT_ELASTICSEARCH_PORT, FASTIOT_ELASTICSEARCH_VOLUME


class NatsService(InfrastructureService):
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
    """ .. _MariaDBService:

    Here, all relevant environment variables are listed to build a MariaDB Service,
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
        )
    ]


class MongoDBService(InfrastructureService):
    """ .. _MongoDBService:

    Here, all relevant environment variables are listed to build a MongoDB Service,
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


class InfluxDBService(InfrastructureService):
    """ .. _InfluxDBService:

    Here, all relevant environment variables are listed to build a InfluxDB Service,
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
    """ .. _TimeScaleDBService:

    Here, all relevant environment variables are listed to build a TimeScaleDB Service,
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
    """ .. _RedisService:

    Here, all relevant environment variables are listed to build a Redis Service,
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


class ElasticSearch(InfrastructureService):
    """ .. _ElasticSearch:

    Here, all relevant environment variables are listed to build an ElasticSearch Service,
    """
    name: str = 'docker.elastic.co/elasticsearch/elasticsearch'
    image: str = 'docker.elastic.co/elasticsearch/elasticsearch:7.17.8'

    host_name_env_var = FASTIOT_ELASTICSEARCH_HOST
    password_env_vars: List[str] = [FASTIOT_ELASTICSEARCH_PASSWORD]

    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=9200,
            default_port_mount=9200,
            env_var=FASTIOT_ELASTICSEARCH_PORT
        )
    ]
    environment: List[InfrastructureServiceEnvVar] = [
        InfrastructureServiceEnvVar(
            name='ELASTIC_PASSWORD',
            default='12345',
            env_var=FASTIOT_ELASTICSEARCH_PASSWORD
        ),
        InfrastructureServiceEnvVar(
            name='ES_JAVA_OPTS',
            default='"-Xmx256m -Xms256m"',
        ),
        InfrastructureServiceEnvVar(
            name='discovery.type',
            default='single-node',
        ),
        InfrastructureServiceEnvVar(
            name='cluster.name',
            default='"single-node-cluster"',
        ),
        InfrastructureServiceEnvVar(
            name='network.host',
            default='0.0.0.0',
        ),
    ]
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/usr/share/elasticsearch/data',
            env_var=FASTIOT_ELASTICSEARCH_VOLUME
        )
    ]
