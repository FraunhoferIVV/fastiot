import os
import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model import Service
from fastiot.cli.model.project import ProjectContext


class TestConfigurationImport(unittest.TestCase):
    def test_smallest_configuration(self):
        with NamedTemporaryFile(suffix='.py') as f:
            f.write(b"project_namespace = 'fastiot_unittest'")
            f.seek(0)

            context = ProjectContext()
            import_configure(context, f.name)

            self.assertEqual('fastiot_unittest', context.project_namespace)
            self.assertEqual(os.getcwd(), context.project_root_dir)
            self.assertEqual('', context.library_package)

    def test_with_service_packages(self):
        with NamedTemporaryFile(suffix='.py', encoding='utf8', mode="w") as f:
            f.write("project_namespace = 'fastiot_unittest'\n")
            f.write(f"project_root_dir = '{os.path.abspath(os.path.join(__file__, '../../../..'))}'\n")
            f.seek(0)

            context = ProjectContext()
            import_configure(context, f.name)

            self.assertEqual('fastiot_unittest', context.project_namespace)
            self.assertIsInstance(context.services[0], Service)
            package_names = [service.package for service in context.services]
            self.assertIn("fastiot_sample_services", package_names)
            self.assertIn("fastiot_core_services", package_names)


if __name__ == '__main__':
    unittest.main()

