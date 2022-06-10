import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.import_configure import import_configure


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


if __name__ == '__main__':
    unittest.main()
