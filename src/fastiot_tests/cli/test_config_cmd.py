import os
import tempfile
import unittest
from glob import glob

from typer.testing import CliRunner

from fastiot.cli import find_deployments
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.infrastructure_service_fn import get_services_list
from fastiot.cli.model import ProjectConfig, Service
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, _import_infrastructure_services
from fastiot.env import FASTIOT_NATS_PORT
from fastiot.helpers.read_yaml import read_config


def _is_in_file(filename, search):
    with open(filename, 'r') as file:
        return search in file.read()


class TestConfigCommand(unittest.TestCase):
    def setUp(self):
        self._initial_cwd = os.getcwd()
        self.assets_dir_ = os.path.join(os.path.dirname(__file__), 'configure_test_assets')
        self.runner = CliRunner()

    def tearDown(self):
        try:
            os.remove(os.path.join(self.assets_dir_, 'src', 'generated.py'))
        except FileNotFoundError:
            pass
        os.chdir(self._initial_cwd)

    def _prepare_env(self, tempdir):

        os.environ['FASTIOT_CONFIGURE_FILE'] = os.path.join(self.assets_dir_, 'configure.py')
        os.chdir(self.assets_dir_)
        default_context = get_default_context()
        default_context.project_config = ProjectConfig(project_namespace='fastiot_tests',
                                                       project_root_dir=self.assets_dir_,
                                                       build_dir=tempdir,
                                                       deployments=find_deployments(path=self.assets_dir_),
                                                       services=[Service(name='dummy_service',
                                                                         package='services')],
                                                       integration_test_deployment='integration_test')
        default_context.external_services = get_services_list()
        _import_infrastructure_services()

    def _parse_docker_compose(self, tempdir, deployment):
        deployments_dir = os.path.join(tempdir, DEPLOYMENTS_CONFIG_DIR)
        docker_compose_file = os.path.join(deployments_dir, deployment, 'docker-compose.yaml')
        self.assertTrue(os.path.isfile(docker_compose_file))

        return read_config(docker_compose_file)

    def test_create_local_test_deployment(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            result = self.runner.invoke(app, ['config', '--test-deployment-only'])
            self.assertEqual(0, result.exit_code)

            # Only one docker-compose created
            deployments_dir = os.path.join(tempdir, DEPLOYMENTS_CONFIG_DIR)
            self.assertEqual(len(glob(os.path.join(deployments_dir, '*', 'docker-compose.yaml'))), 1)
            docker_compose = self._parse_docker_compose(tempdir, 'integration_test')

            # No port changes
            self.assertEqual(docker_compose['x-env'][FASTIOT_NATS_PORT], '4222')
            self.assertEqual(docker_compose['services']['nats']['ports'][0], '4222:4222')

            # Tmpfs instead of volume
            self.assertTrue('tmpfs' in docker_compose['services']['mongodb'])
            self.assertFalse('volumes' in docker_compose['services']['mongodb'])

    def test_create_deployment_with_port_change(self):
        """ Changing ports """
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            result = self.runner.invoke(app, ['config', '--test-deployment-only', '--service-port-offset=1000'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'integration_test')
            self.assertEqual(docker_compose['x-env'][FASTIOT_NATS_PORT], '4222')  # Config for internal stays
            self.assertEqual(docker_compose['services']['nats']['ports'][0], '1000:4222')  # External port changes

            os.environ[FASTIOT_NATS_PORT] = '2000'
            self.runner.invoke(app, ['config', '--test-deployment-only', '--service-port-offset=1000'])
            docker_compose = self._parse_docker_compose(tempdir, 'integration_test')
            self.assertEqual(docker_compose['x-env'][FASTIOT_NATS_PORT], '4222')  # Config for internal stays
            # External port changes to offset, not to environment variable
            self.assertEqual(docker_compose['services']['nats']['ports'][0], '1000:4222')
            os.environ.pop(FASTIOT_NATS_PORT)

    def test_dot_env_does_not_change_ports(self):
        """ If the user explicitly asks for new ports the .env should not be read """
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            result = self.runner.invoke(app, ['config', '--service-port-offset=1000', 'only_dot_env'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'only_dot_env')
            self.assertEqual('4222', docker_compose['x-env'][FASTIOT_NATS_PORT])  # Config for internal stays
            # External port changes to offset, not to .env
            self.assertEqual('1000:4222', docker_compose['services']['nats']['ports'][0])

    def test_change_ports_with_env_vars(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)
            os.environ[FASTIOT_NATS_PORT] = '1000'

            result = self.runner.invoke(app, ['config', 'only_dot_env', 'per_service_env'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'per_service_env')
            self.assertEqual('1000:4222', docker_compose['services']['nats']['ports'][0])

            docker_compose = self._parse_docker_compose(tempdir, 'only_dot_env')
            self.assertEqual('1000:4222', docker_compose['services']['nats']['ports'][0],
                             "Should use the variable set env var and not the .env file")
            os.environ.pop(FASTIOT_NATS_PORT)


    def test_change_ports_with_dot_env(self):
        with tempfile.TemporaryDirectory() as tempdir:
            self._prepare_env(tempdir)

            result = self.runner.invoke(app, ['config', 'only_dot_env', 'per_service_env'])
            self.assertEqual(0, result.exit_code)

            docker_compose = self._parse_docker_compose(tempdir, 'per_service_env')
            self.assertEqual('4222:4222', docker_compose['services']['nats']['ports'][0],
                             "Use default port for nats")

            docker_compose = self._parse_docker_compose(tempdir, 'only_dot_env')
            self.assertEqual('2000:4222', docker_compose['services']['nats']['ports'][0],
                             "Should use the variable set .env var")

if __name__ == '__main__':
    unittest.main()
