from fastiot.cli.model import ExternalService


class NatsService(ExternalService):
    name = 'nats'
    docker_image = 'nats:latest'
    port = 4222
    port_env_var = 'FASTIOT_NATS_PORT'


class MariaDBService(ExternalService):
    name = 'mariadb'
    docker_image = 'mariadb:10.8'
    port = 3306
    port_env_var = 'FASTIOT_MARIADB_PORT'


class MongoDBService(ExternalService):
    name = 'mongodb'
    docker_image = 'mongodb:4.4'
    port = 27017
    port_env_var = 'FASTIOT_MONGODB_PORT'
