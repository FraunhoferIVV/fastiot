import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.model.deployment import DeploymentConfig
from fastiot.testlib.cli import init_default_context

DEPLOYMENT_CONFIG = """
x-env1: &env_machine1
  FASTIOT_MACHINE_ID: machine1
  FASTIOT_OPCUA_ENDPOINT_URL: 'opc.tcp://sam_packaging_sealing_demo_control1:4840/simMachine/'

x-env2: &env_machine2
  FASTIOT_MACHINE_ID: machine2
  FASTIOT_OPCUA_ENDPOINT_URL: 'opc.tcp://sam_packaging_sealing_demo_control2:4841/simMachine/'

services:
  fastiot/time_series:
  ml_module1:
    image: fastiot/machine_learning
    environment:
      <<: *env_machine1
    tag: latest
  ml_module2:
    image: fastiot/machine_learning
    environment:
      <<: *env_machine2
      FASTIOT_LOG_LEVEL_NO: 20 # DEBUG

infrastructure_services:
  nats:
  mongodb:
  mariadb:

config_dir: ./config_dir

environment:
  FASTIOT_CUSTOMER: packaging_sealing_demo
  FASTIOT_MACHINE_ID: machine1
  FASTIOT_LOG_LEVEL_NO: 20

docker_registry: "docker.dev.ivv-dd.fhg.de"
"""


class TestDeployment(unittest.TestCase):

    def setUp(self):
        init_default_context()

    def test_yaml_parsing(self):
        with NamedTemporaryFile(mode="w") as file:
            file.write(DEPLOYMENT_CONFIG)
            file.seek(0)
            deployment = DeploymentConfig.from_yaml_file(filename=file.name)
            self.assertIsInstance(deployment, DeploymentConfig)


if __name__ == '__main__':
    unittest.main()
