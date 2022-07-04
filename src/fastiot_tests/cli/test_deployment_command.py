import os
import tempfile
import unittest

from typer.testing import CliRunner

from fastiot.cli.constants import GENERATED_DEPLOYMENTS_DIR, DEPLOYMENTS_CONFIG_FILE, DEPLOYMENTS_CONFIG_DIR
from fastiot.cli.typer_app import app
from fastiot.testlib.cli import init_default_context
from fastiot_tests.cli.test_build_command import _prepare_env

DEPLOYMENT_EXAMPLE = """
deployment_name: fastiot_unittest
deployment_target:
  hosts:
    localhost:
      ip: 127.0.0.1
"""


class TestDeploymentCommand(unittest.TestCase):
    def setUp(self):
        self._old_cwd = os.getcwd()
        # Change to some arbitrary path where :func:`fastiot.cli.import_configure.import_configure` will not directly
        # find some deployments (s. #16795 for more details)
        os.chdir('/tmp')
        self.runner = CliRunner()

    def tearDown(self):
        os.chdir(self._old_cwd)

    def test_no_service(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir, project_root_dir=tempdir)

            result = self.runner.invoke(app, ["deploy", "--dry", "fastiot_unittest"])
            self.assertEqual(1, result.exit_code)
            self.assertTrue('not in project deployments' in result.stdout)

    def test_no_target(self):
        with tempfile.TemporaryDirectory() as tempdir:
            os.chdir(tempdir)
            deployments_dir = os.path.join(tempdir, DEPLOYMENTS_CONFIG_DIR, 'fastiot_unittest')
            os.makedirs(deployments_dir, exist_ok=True)
            with open(os.path.join(deployments_dir, DEPLOYMENTS_CONFIG_FILE), 'w') as file:
                file.write("fastiot_services: []")
            _prepare_env(tempdir, project_root_dir=tempdir)

            result = self.runner.invoke(app, ["deploy", "--dry", "fastiot_unittest"])

            self.assertEqual(2, result.exit_code)
            self.assertTrue('does not have a deployment_target' in result.stdout)

    def test_single_service(self):
        with tempfile.TemporaryDirectory() as tempdir:
            deployments_dir = os.path.join(tempdir, DEPLOYMENTS_CONFIG_DIR, 'fastiot_unittest')
            os.makedirs(deployments_dir, exist_ok=True)
            with open(os.path.join(deployments_dir, DEPLOYMENTS_CONFIG_FILE), 'w') as file:
                file.write(DEPLOYMENT_EXAMPLE)
            _prepare_env(tempdir, project_root_dir=tempdir)

            result = self.runner.invoke(app, ["deploy", "--dry", "fastiot_unittest"])

            self.assertEqual(0, result.exit_code)

            generated_path = os.path.join(tempdir, GENERATED_DEPLOYMENTS_DIR, "fastiot_unittest")
            for file in ['ansible-playbook.yaml', 'hosts']:
                self.assertTrue(os.path.isfile(os.path.join(generated_path, file)))


if __name__ == '__main__':
    unittest.main()
