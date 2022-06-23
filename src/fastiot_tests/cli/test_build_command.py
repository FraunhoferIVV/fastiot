import os.path
import tempfile
import unittest

from typer.testing import CliRunner

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.context import get_default_context
from fastiot.cli.typer_app import app
from fastiot.testlib.cli import init_default_context
from fastiot.cli.commands import *  # noqa  # pylint: disable=wildcard-import,unused-wildcard-import


def _write_configure(path: str):
    configure_file = os.path.join(path, 'configure.py')
    with open(configure_file, 'w') as file:
        file.write("from fastiot.cli.model import ModulePackageConfig\n"
                   "project_namespace = 'fastiot'\n"
                   f"project_root_dir = '{os.path.abspath(os.path.join(__file__, '..', '..', '..', '..'))}'\n"
                   "module_packages = [ModulePackageConfig(package_name='fastiot_sample_services')]\n"
                   f"build_dir='{path}'\n"
                   "test_config = 'fastiot_test_env'\n")
        file.seek(0)

def _prepare_env(tempdir):
    _write_configure(tempdir)
    os.environ['FASTIOT_CONFIGURE_FILE'] = os.path.join(tempdir, 'configure.py')
    default_context = get_default_context()
    default_context.project_config = import_configure(os.environ.get('FASTIOT_CONFIGURE_FILE'))
        
class TestBuildCommand(unittest.TestCase):

    def setUp(self):
        init_default_context()
        self.runner = CliRunner()



    def test_single_module(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)

            result = self.runner.invoke(app, ["build", "--dry", "producer"])

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.isfile(os.path.join(tempdir, 'docker-bake.hcl')))
            self.assertTrue(os.path.isfile(os.path.join(tempdir, 'Dockerfile.producer')))
            self.assertFalse(os.path.isfile(os.path.join(tempdir, 'Dockerfile.consumer')))

    def test_all_modules(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)

            result = self.runner.invoke(app, ["build", "--dry"])

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(os.path.isfile(os.path.join(tempdir, 'Dockerfile.producer')))
            self.assertTrue(os.path.isfile(os.path.join(tempdir, 'Dockerfile.consumer')))

    def test_docker_registry_per_env(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            os.environ['FASTIOT_DOCKER_REGISTRY'] = 'TEST_REGISTRY'

            result = self.runner.invoke(app, ["build", "--dry"])
            self.assertEqual(result.exit_code, 0)

            with open(os.path.join(tempdir, 'docker-bake.hcl'), 'r') as f:
                self.assertTrue('TEST_REGISTRY' in f.read())

    def test_docker_registry_per_argument(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)
            # os.environ['FASTIOT_DOCKER_REGISTRY'] = 'TEST_REGISTRY'

            result = self.runner.invoke(app, ["build", "--dry", "--docker-registry=TEST_REGISTRY"])
            self.assertEqual(result.exit_code, 0)
            with open(os.path.join(tempdir, 'docker-bake.hcl'), 'r') as f:
                self.assertTrue('TEST_REGISTRY' in f.read())

    def test_no_local_cache_if_pushing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)

            result = self.runner.invoke(app, ["build", "--dry", "--push"])
            self.assertEqual(result.exit_code, 0)
            with open(os.path.join(tempdir, 'docker-bake.hcl'), 'r') as f:
                contents = f.read()
                self.assertFalse('"type=local,src=.docker-cache"' in contents)
                self.assertTrue('cache-to= [ "type=registry,' in contents)

    def test_local_cache_if_not_pushing(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)

            result = self.runner.invoke(app, ["build", "--dry"])
            self.assertEqual(result.exit_code, 0)
            with open(os.path.join(tempdir, 'docker-bake.hcl'), 'r') as f:
                contents = f.read()
                self.assertTrue('"type=local,src=.docker-cache"' in contents)
                self.assertFalse('cache-to= [ "type=registry,' in contents)

    def test_build_empty_test_env(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir)

            result = self.runner.invoke(app, ["build", "--dry", "--test-env-only"])
            self.assertEqual(result.exit_code, 0)
            self.assertFalse(os.path.isfile(os.path.join(tempdir, 'docker-bake.hcl')))


if __name__ == '__main__':
    unittest.main()
