import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.model.manifest import ModuleManifest

MANIFEST = """
fastiot_module:
  name: data_dashboard

  mount_config_dir: required

  ports:
    http:
      location: 5802
      env_variable: SAM_DASHBOARD_PORT

  depends_on:
    - mongodb
    - nats

  platforms: [ amd64, arm64 ]

"""


class TestManifest(unittest.TestCase):

    def test_yaml_parsing(self):

        with NamedTemporaryFile(mode="w") as file:
            file.write(MANIFEST)
            file.seek(0)
            manifest = ModuleManifest.from_yaml_file(filename=file.name)
            self.assertIsInstance(manifest, ModuleManifest)

    def test_docker_name_parser(self):

        invalid_docker_names = [';do_stuff.sh;', 'image:latest&do-stuff']
        for invalid_name in invalid_docker_names:
            with self.assertRaises(ValueError):
                ModuleManifest.from_docker_image(invalid_name)


if __name__ == '__main__':
    unittest.main()
