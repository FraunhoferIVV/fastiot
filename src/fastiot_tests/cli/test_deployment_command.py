import os
import tempfile
import unittest

from typer.testing import CliRunner

from fastiot.cli.constants import GENERATED_DEPLOYMENTS_DIR
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
        init_default_context()
        self.runner = CliRunner()

    def test_single_module(self):
        with tempfile.TemporaryDirectory() as tempdir:
            _prepare_env(tempdir, project_root_dir=tempdir)

            deployments_dir = os.path.join(tempdir, 'deployments', 'fastiot_unittest')
            os.makedirs(deployments_dir, exist_ok=True)
            with open(os.path.join(deployments_dir, 'deployment.yaml'), 'w') as file:
                file.write(DEPLOYMENT_EXAMPLE)

            result = self.runner.invoke(app, ["deploy", "--dry", "fastiot_unittest"])

            self.assertEqual(result.exit_code, 0)

            generated_path = os.path.join(tempdir, GENERATED_DEPLOYMENTS_DIR, "fastiot_unittest")
            for file in ['ansible-playbook.yaml', 'hosts']:
                self.assertTrue(os.path.isfile(os.path.join(generated_path, file)))


if __name__ == '__main__':
    unittest.main()
