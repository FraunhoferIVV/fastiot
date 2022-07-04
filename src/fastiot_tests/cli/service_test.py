from fastiot.cli.model import InfrastructureService


class SomeTestService(InfrastructureService):
    name = 'test_service'
    docker_image = 'test'
    port = 1
    port_env_var = 'TEST_PORT'
