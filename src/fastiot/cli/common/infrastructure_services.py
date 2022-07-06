from typing import List

from fastiot.cli.model import InfrastructureService
from fastiot.cli.model.service import InfrastructureServicePort


class NatsService(InfrastructureService):
    name: str = 'nats'
    image: str = 'nats:latest'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=4222,
            default_port_mount=4222,
            env_var='FASTIOT_NATS_PORT'
        )
    ]


#class MariaDBService(InfrastructureService):
#    name = 'mariadb'
#    image = 'mariadb:10.8'
#    port = 3306
#    port_env_var = 'FASTIOT_MARIADB_PORT'
#
#
#class MongoDBService(InfrastructureService):
#    name = 'mongodb'
#    image = 'mongodb:4.4'
#    port = 27017
#    port_env_var = 'FASTIOT_MONGODB_PORT'
