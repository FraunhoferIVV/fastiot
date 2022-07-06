from typing import List

from fastiot.cli.model import InfrastructureService
from fastiot.cli.model.service import InfrastructureServicePort, InfrastructureServiceEnvVar, \
    InfrastructureServiceVolume
from fastiot.env import FASTIOT_NATS_PORT, FASTIOT_MARIA_DB_PORT, FASTIOT_MONGO_DB_PORT, FASTIOT_MONGO_DB_USER, \
    FASTIOT_MONGO_DB_PASSWORD, FASTIOT_MARIA_DB_PASSWORD, FASTIOT_MONGO_DB_VOLUME, FASTIOT_MARIA_DB_VOLUME


class NatsService(InfrastructureService):
    name: str = 'nats'
    image: str = 'nats:latest'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=4222,
            default_port_mount=4222,
            env_var=FASTIOT_NATS_PORT
        )
    ]


class MariaDBService(InfrastructureService):
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
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/var/lib/mysql',
            default_volume_mount='/var/fastiot/volumes/fastiot_dev/mariadb',
            env_var=FASTIOT_MARIA_DB_VOLUME
        )
    ]


class MongoDBService(InfrastructureService):
    name: str = 'mongodb'
    image: str = 'mongodb:4.4-bionic'
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
    volumes: List[InfrastructureServiceVolume] = [
        InfrastructureServiceVolume(
            container_volume='/data/db',
            default_volume_mount='/var/fastiot/volumes/fastiot_dev/mongodb',
            env_var=FASTIOT_MONGO_DB_VOLUME
        )
    ]
