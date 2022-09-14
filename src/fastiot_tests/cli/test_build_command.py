import os
import os.path
import tempfile
import unittest
from typing import Optional

from typer.testing import CliRunner

from fastiot.cli.constants import DOCKER_BUILD_DIR
from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.context import get_default_context
from fastiot.cli.model.project import ProjectConfig
from fastiot.cli.typer_app import app
from fastiot.testlib.cli import init_default_context
from fastiot.cli.commands import *  # noqa  # pylint: disable=wildcard-import,unused-wildcard-import


def _write_configure(path: str, no_services: bool, project_root_dir: Optional[str]):
    configure_file = os.path.join(path, 'configure.py')
    if no_services:
        project_root_dir = '/tmp'
    else:
        project_root_dir = project_root_dir or os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))
    with open(configure_file, 'w') as file:
        file.write("project_namespace = 'fastiot'\n"
                   f"project_root_dir = '{project_root_dir}'\n"
                   f"build_dir = '{path}'\n"
                   "integration_test_deployment = 'integration_test'\n")

        file.seek(0)


def _prepare_env(tempdir, no_services=False, project_root_dir:str = None):
    _write_configure(tempdir, no_services, project_root_dir)
    os.environ['FASTIOT_CONFIGURE_FILE'] = os.path.join(tempdir, 'configure.py')
    default_context = get_default_context()
    default_context.project_config = ProjectConfig()
    import_configure(default_context.project_config, os.environ.get('FASTIOT_CONFIGURE_FILE', ''))


class TestBuildCommand(unittest.TestCase):

    def setUp(self):
        init_default_context()
        self.runner = CliRunner()

    def test_single_service(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            result = self.runner.invoke(app, ["build", "--dry", "producer"], catch_exceptions=False)

            self.assertEqual(0, result.exit_code)
            self.assertTrue(os.path.isfile(os.path.join(docker_dir, 'docker-bake.hcl')))
            self.assertTrue(os.path.isfile(os.path.join(docker_dir, 'Dockerfile.producer')))
            self.assertFalse(os.path.isfile(os.path.join(docker_dir, 'Dockerfile.consumer')))

    def test_all_services(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            result = self.runner.invoke(app, ["build", "--dry"], catch_exceptions=False)

            self.assertEqual(0, result.exit_code)
            self.assertTrue(os.path.isfile(os.path.join(docker_dir, 'Dockerfile.producer')))
            self.assertTrue(os.path.isfile(os.path.join(docker_dir, 'Dockerfile.consumer')))

    def test_docker_registry_per_env(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            os.environ['FASTIOT_DOCKER_REGISTRY'] = 'TEST_REGISTRY'

            result = self.runner.invoke(app, ["build", "--dry"], catch_exceptions=False)
            self.assertEqual(0, result.exit_code)

            with open(os.path.join(docker_dir, 'docker-bake.hcl'), 'r') as f:
                self.assertTrue('TEST_REGISTRY' in f.read())

    def test_docker_registry_per_argument(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            result = self.runner.invoke(app, ["build", "--dry", "--docker-registry=TEST_REGISTRY"], catch_exceptions=False)
            self.assertEqual(0, result.exit_code)
            with open(os.path.join(docker_dir, 'docker-bake.hcl'), 'r') as f:
                self.assertTrue('TEST_REGISTRY' in f.read())

    def test_no_local_cache_if_pushing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            result = self.runner.invoke(app, ["build", "--dry", "--push", "--docker-registry", "test_registry", "--docker-registry-cache", "test_cache_registry"], catch_exceptions=False)
            self.assertEqual(0, result.exit_code)
            with open(os.path.join(docker_dir, 'docker-bake.hcl'), 'r') as f:
                contents = f.read()
                self.assertFalse('"type=local,src=.docker-cache"' in contents)
                self.assertTrue('cache-to = [ "type=registry,' in contents)

    def test_local_cache_if_not_pushing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            result = self.runner.invoke(app, ["build", "--dry"], catch_exceptions=False)
            self.assertEqual(0, result.exit_code)
            with open(os.path.join(docker_dir, 'docker-bake.hcl'), 'r') as f:
                contents = f.read()
                self.assertTrue('"type=local,src=.docker-cache"' in contents)
                self.assertFalse('cache-to = [ "type=registry,' in contents)

    def test_build_empty_test_env(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            result = self.runner.invoke(app, ["build", "--dry", "--test-deployment-only"], catch_exceptions=False)
            self.assertEqual(0, result.exit_code)
            self.assertFalse(os.path.isfile(os.path.join(docker_dir, 'docker-bake.hcl')))

    def test_empty_build(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir, no_services=True)
            docker_dir = os.path.join(tempdir, DOCKER_BUILD_DIR)

            result = self.runner.invoke(app, ["build", "--dry"], catch_exceptions=False)
            self.assertEqual(0, result.exit_code)
            self.assertFalse(os.path.isfile(os.path.join(docker_dir, 'docker-bake.hcl')))
            self.assertFalse(os.path.isfile(os.path.join(docker_dir, 'Dockerfile.producer')))
            self.assertFalse(os.path.isfile(os.path.join(docker_dir, 'Dockerfile.consumer')))


if __name__ == '__main__':
    unittest.main()
