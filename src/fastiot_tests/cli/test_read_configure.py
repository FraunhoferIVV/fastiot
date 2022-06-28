import os
import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model import ModuleConfig


class TestConfigurationImport(unittest.TestCase):
    def test_smallest_configuration(self):
        with NamedTemporaryFile(suffix='.py') as f:
            f.write(b"project_namespace = 'fastiot_unittest'")
            f.seek(0)

            config = import_configure(f.name)

            self.assertEqual(config.project_namespace, 'fastiot_unittest')
            self.assertEqual(config.project_root_dir, os.getcwd())
            self.assertIsNone(config.library_package)

    def test_missing_configuration_option(self):
        with NamedTemporaryFile(suffix='.py') as f:
            with self.assertRaises(ValueError):
                _ = import_configure(f.name)

    def test_with_module_packages(self):
        with NamedTemporaryFile(suffix='.py') as f:
            f.write(b"from fastiot.cli import find_modules\n"
                    b"project_namespace = 'fastiot_unittest'\n"
                    b"modules = [*find_modules(package='fastiot_sample_services')]")
            f.seek(0)

            config = import_configure(f.name)

            self.assertEqual(config.project_namespace, 'fastiot_unittest')
            self.assertIsInstance(config.modules[0], ModuleConfig)
            self.assertEqual(config.modules[0].package, "fastiot_sample_services")


if __name__ == '__main__':
    unittest.main()
