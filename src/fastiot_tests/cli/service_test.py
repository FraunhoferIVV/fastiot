from typing import List

from fastiot.cli.model.infrastructure_service import InfrastructureService, InfrastructureServicePort


class SomeTestService(InfrastructureService):
    name = 'test_service'
    image = 'test'
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=1,
            default_port_mount=1,
            env_var='TEST_PORT'
        )
    ]
