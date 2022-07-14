import os
import tempfile
import unittest
from glob import glob

import compose as compose
import docker as docker
from typer.testing import CliRunner

from fastiot.cli import find_deployments
from fastiot.cli.constants import DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.infrastructure_service_fn import get_services_list
from fastiot.cli.model import ProjectConfig
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app, _import_infrastructure_services


def _prepare_env(tempdir):
    assets_dir = os.path.join(os.path.dirname(__file__), 'configure_test_assets')
    os.environ['FASTIOT_CONFIGURE_FILE'] = os.path.join(assets_dir, 'configure.py')
    os.chdir(assets_dir)
    default_context = get_default_context()
    default_context.project_config = ProjectConfig(project_namespace='fastiot_tests',
                                                   project_root_dir=assets_dir,
                                                   build_dir=tempdir,
                                                   deployments=find_deployments(path=assets_dir),
                                                   integration_test_deployment='integration_test')
    default_context.external_services = get_services_list()
    _import_infrastructure_services()


def _is_in_file(filename, search):
    with open(filename, 'r') as file:
        return search in file.read()


class TestConfigCommand(unittest.TestCase):
    def setUp(self):
        self._initial_cwd = os.getcwd()

        self.runner = CliRunner()

    def tearDown(self):
        os.chdir(self._initial_cwd)

    def test_create_local_test_deployment(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            result = self.runner.invoke(app, ['config', '--test-deployment-only'])
            self.assertEqual(0, result.exit_code)

            deployments_dir = os.path.join(tempdir, DEPLOYMENTS_CONFIG_DIR)
            # Only one docker-compose created
            self.assertEqual(len(glob(os.path.join(deployments_dir, '*', 'docker-compose.yaml'))), 1)

            docker_compose_file = os.path.join(deployments_dir, 'integration_test', 'docker-compose.yaml')
            self.assertTrue(os.path.isfile(docker_compose_file))

            # No port changes
            self.assertTrue(_is_in_file(docker_compose_file, "27017:27017"))

            # Tmpfs instead of volume
            self.assertTrue(_is_in_file(docker_compose_file, "tmpfs:"))
            self.assertFalse(_is_in_file(docker_compose_file, "volumes:"))


if __name__ == '__main__':
    unittest.main()
