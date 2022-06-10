import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model import ModulePackageConfig


class TestConfigurationImport(unittest.TestCase):
    def test_smallest_configuration(self):
        with NamedTemporaryFile(suffix='.py') as f:
            f.write(b"project_namespace = 'fastiot_unittest'")
            f.seek(0)

            config = import_configure(f.name)

            self.assertEqual(config.project_namespace, 'fastiot_unittest')
            self.assertIsNone(config.library_package)

    def test_missing_configuration_option(self):
        with NamedTemporaryFile(suffix='.py') as f:
            with self.assertRaises(ValueError):
                _ = import_configure(f.name)

    def test_with_module_packages(self):
        with NamedTemporaryFile(suffix='.py') as f:
            f.write(b"from fastiot.cli.model import ModulePackageConfig\n"
                    b"project_namespace = 'fastiot_unittest'\n"
                    b"module_packages = [ModulePackageConfig(package_name='fastiot_samples', module_names=[])]")
            f.seek(0)

            config = import_configure(f.name)

            self.assertEqual(config.project_namespace, 'fastiot_unittest')
            self.assertTrue(type(config.module_packages), ModulePackageConfig)
            self.assertEqual(config.module_packages[0].package_name, "fastiot_samples")


if __name__ == '__main__':
    unittest.main()
