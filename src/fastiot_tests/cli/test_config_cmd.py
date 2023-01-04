import os
import tempfile
import unittest
from glob import glob
from typing import List

from typer.testing import CliRunner

from fastiot.cli import find_deployments
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR, FASTIOT_CONFIGURE_FILE
from fastiot.cli.model import ProjectContext, Service, InfrastructureService
from fastiot.cli.model.infrastructure_service import InfrastructureServicePort
from fastiot.cli.typer_app import app, _import_infrastructure_services
from fastiot.util.read_yaml import read_config

FASTIOT_AAASERVICE_PORT = 'FASTIOT_AAASERVICE_PORT'
FASTIOT_AAASERVICE_HOST = 'FASTIOT_AAASERVICE_HOST'


class AAAService(InfrastructureService):
    name: str = 'aaa'
    image: str = 'hello-world:latest'
    host_name_env_var = FASTIOT_AAASERVICE_HOST
    ports: List[InfrastructureServicePort] = [
        InfrastructureServicePort(
            container_port=5222,
            default_port_mount=5222,
            env_var=FASTIOT_AAASERVICE_PORT
        )
    ]


class TestConfigCommand(unittest.TestCase):
    def setUp(self):
        self._backup_context = ProjectContext.default.copy(deep=True)
        self._initial_cwd = os.getcwd()
        self.assets_dir_ = os.path.join(os.path.dirname(__file__), 'configure_test_assets')
        self.runner = CliRunner()

    def tearDown(self):
        os.chdir(self._initial_cwd)
        if FASTIOT_CONFIGURE_FILE in os.environ:
            del os.environ[FASTIOT_CONFIGURE_FILE]
        ProjectContext._default_context = self._backup_context

    def _prepare_env(self, tempdir):

        os.environ[FASTIOT_CONFIGURE_FILE] = os.path.join(self.assets_dir_, 'configure.py')
        os.chdir(self.assets_dir_)
        default_context = ProjectContext.default
        default_context.project_namespace = 'fastiot_tests'
        default_context.project_root_dir = self.assets_dir_
        default_context.build_dir = tempdir
        default_context.deployments = find_deployments(path=self.assets_dir_)
        default_context.services = [Service(name='dummy_service', package='services')]
        default_context.integration_test_deployment = 'integration_test'
        _import_infrastructure_services()

    def _parse_docker_compose(self, tempdir, deployment):
        deployments_dir = os.path.join(tempdir, DEPLOYMENTS_CONFIG_DIR)
        docker_compose_file = os.path.join(deployments_dir, deployment, 'docker-compose.yaml')
        self.assertTrue(os.path.isfile(docker_compose_file))

        return read_config(docker_compose_file)

    def test_create_local_test_deployment(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            result = self.runner.invoke(app, ['config', '--use-test-deployment'])
            self.assertEqual(0, result.exit_code)

            # Only one docker-compose created
            deployments_dir = os.path.join(tempdir, DEPLOYMENTS_CONFIG_DIR)
            self.assertEqual(1, len(glob(os.path.join(deployments_dir, '*', 'docker-compose.yaml'))))
            docker_compose = self._parse_docker_compose(tempdir, 'integration_test')

            # No port changes
            self.assertEqual('5222', docker_compose['x-env'][FASTIOT_AAASERVICE_PORT])
            self.assertEqual('5222:5222', docker_compose['services']['aaa']['ports'][0])

            # Tmpfs instead of volume
            # self.assertTrue('tmpfs' in docker_compose['services']['mongodb'])
            # self.assertFalse('volumes' in docker_compose['services']['mongodb'])

    @unittest.skip("Unclear what this should do")
    def test_create_deployment_with_port_change(self):
        """ Changing ports """
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            result = self.runner.invoke(app, ['config', '--use-test-deployment', '--port-offset=1000'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'integration_test')
            self.assertEqual('5222', docker_compose['x-env'][FASTIOT_AAASERVICE_PORT])  # Config for internal stays
            self.assertEqual('1000:5222', docker_compose['services']['aaa']['ports'][0])  # External port changes

            os.environ[FASTIOT_AAASERVICE_PORT] = '2000'
            self.runner.invoke(app, ['config', '--use-test-deployment', '--port-offset=1000'])
            docker_compose = self._parse_docker_compose(tempdir, 'integration_test')
            self.assertEqual(docker_compose['x-env'][FASTIOT_AAASERVICE_PORT], '5222')  # Config for internal stays
            # External port changes to offset, not to environment variable
            self.assertEqual('1000:5222', docker_compose['services']['aaa']['ports'][0])
            os.environ.pop(FASTIOT_AAASERVICE_PORT)

    @unittest.skip("Not needed anymore")
    def test_dot_env_does_not_change_ports(self):
        """ If the user explicitly asks for new ports the .env should not be read """
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            result = self.runner.invoke(app, ['config', '--port-offset=1000', 'only_dot_env'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'only_dot_env')
            self.assertEqual('5222', docker_compose['x-env'][FASTIOT_AAASERVICE_PORT])  # Config for internal stays
            # External port changes to offset, not to .env
            self.assertEqual('1000:5222', docker_compose['services']['aaa']['ports'][0])

    @unittest.skip("")
    def test_change_ports_with_env_vars(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            os.environ[FASTIOT_AAASERVICE_PORT] = '1000'

            result = self.runner.invoke(app, ['config', 'only_dot_env', 'per_service_env'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'per_service_env')
            self.assertEqual('1000:5222', docker_compose['services']['aaa']['ports'][0])

            docker_compose = self._parse_docker_compose(tempdir, 'only_dot_env')
            self.assertEqual('1000:5222', docker_compose['services']['aaa']['ports'][0],
                             "Should use the variable set env var and not the .env file")
            os.environ.pop(FASTIOT_AAASERVICE_PORT)

    def test_change_ports_with_dot_env(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)

            result = self.runner.invoke(app, ['config', 'only_dot_env', 'per_service_env'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'per_service_env')
            self.assertEqual('5222:5222', docker_compose['services']['aaa']['ports'][0],
                             "Use default port for nats")

            docker_compose = self._parse_docker_compose(tempdir, 'only_dot_env')
            self.assertEqual('2000:5222', docker_compose['services']['aaa']['ports'][0],
                             "Should use the variable set .env var")


if __name__ == '__main__':
    unittest.main()
