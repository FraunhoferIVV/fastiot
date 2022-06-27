""" Data model for module manifests """
import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from shlex import quote as shlex_quote
from typing import List, Dict, Optional

import yaml
from pydantic.main import BaseModel

from fastiot.cli.constants import DOCKER_BASE_IMAGE
from fastiot.cli.helper_fn import get_cli_logger


class Port(BaseModel):
    """
    A port entry represents one port used by the module which should be mounted outside the container.
    """

    location: int
    """
    The default port location.
    """
    env_variable: str
    """
    The environment variable which is passed to the container to change the port, e.g. for automated testing.
    """


class Volume(BaseModel):
    """
    A volume entry represents one directory used by the module which should be mounted outside the container.
    """

    location: str
    """
    The volume location to be used. If you provide something like :file:`/opt/mydata` it will be accessible as
    file:`opt/mydata` in  your container.
    """
    env_variable: str
    """
    See attribute `env_variable` in :class:`fastiot.cli.model.manifest.Port`.
    """


@dataclass
class Device:
    """
    A device entry represents one device used by the module which should be mounted outside the container.
    """

    location: str
    """
    The default device location, e.g. :file:`/dev/ttyS0` for a serial port
    """
    env_variable: str
    """
    See attribute `env_variable` in :class:`fastiot.cli.model.manifest.Port`.
    """


class MountConfigDirEnum(str, Enum):
    """ Set if the configuration dir needs to be mounted in the container """
    required = "required"  # This will make the config dir available through the docker-compose file.
    optional = "optional"


class CPUPlatform(str, Enum):
    """ Definition of the CPU platform the container will be built for """

    amd64 = "amd64"  # The most common architecture for servers, desktop and laptop computers with Intel or AMD CPUs.
    amd64_2 = "amd64_2"  # Use more CPU features, s. https://en.wikipedia.org/wiki/X86-64#Microarchitecture_levels
    arm64 = "arm64"  # Modern architecture for e.g. Raspberry Pi 3 and 4 if a 64 Bit OS is used like Ubuntu 20.04
    armv7 = 'armv7'  # 32bit ARM like RasPi with 32 bit OS

    def as_docker_platform(self):
        """ Returns a member (accessed by self in this case!) as docker-style platform. This usually means e.g.
        `linux/amd64`"""
        if self == self.amd64_2:
            return "linux/amd64/2"
        elif self == self.armv7:
            return 'linux/arm/v7'
        return "linux/" + self


class Healthcheck(str, Enum):
    """ TODO: Add some description here! """
    error_log = "error_log"


class Vue(BaseModel):
    """ Use this part if your project contains a frontend created with vue.js """

    src: str  # Source path relative to your application where the vue.js code is located
    dst: str  # Destination path where the build static files will be placed, e.g. 'static'
    configured_dist: str = 'dist'
    """ Destination where vue.js will place its files for distribution. If not changed vue.js will have save its files
    in the `<vue-path>/dist` which is also the default here.
    If you have something like
    ``
    module.exports = {
      outputDir:"../flask_server/static",
      assetsDir: "static"
    }
    ``
    in your :file:`vue.config.js` use the `outputDir` variable as relative path here.
    """


class ModuleManifest(BaseModel):
    """
    Manifest files may contain these variables.
    :any:`fastiot.cli.model.manifest.ModuleManifest.name` is needed, others are mostly optional!
    """
    name: str  # Name needs to comply with the modules name
    ports: Optional[Dict[str, Port]] = None
    """
    Provide a list with some name for the service and a port that this container will open, e.g. when operating
    as a webserver.`
    """
    docker_base_image: str = DOCKER_BASE_IMAGE
    """ Use this to provide an alternative base image, otherwise
    :const:`fastiot.cli.constants.DOCKER_BASE_IMAGE` will be used.
    
    Be aware, that the further Dockerfile will be unchanged, thus your base image should be based on some Debian-style.
    If this does not work for you, you may also provide a :file:`Dockerfile` in your module which will automatically be
    used.
    """
    docker_cache_image: Optional[str] = None
    """ If set this will override the per module package configuration for a docker registry cache. The full cache name
    will be constructed from the docker cache registry set and this name. """
    volumes: Optional[Dict[str, Volume]] = None  # Volumes to be mounted in the container
    devices: Optional[Dict[str, Device]] = None  # Devices, e.g. serial devices, to be mounted in the container
    mount_config_dir: MountConfigDirEnum = MountConfigDirEnum.required
    # depends_on: List[ServiceEnum] = ()
    privileged: bool = False
    """
    Enable if this module needs privileged permissions inside docker, e.g. for hardware access
    """
    platforms: List[CPUPlatform] = [CPUPlatform.amd64]
    """ Define the cpu platforms to build the container for. It defaults to amd64. If doing local builds the first one
    specified (or amd64 if none) will be used to build the image. """

    healthcheck: Optional[Healthcheck] = None  # Configure healthcheck for the container
    copy_dirs_to_container: List[str] = ()
    """
    Directories which shall be copied to container. They must be specified relative to manifest.yaml.
    """

    vue: Optional[Vue] = None
    """
    If your project contains a vue.js application you can automatically build it here. For required configuration
    s ::class:`Vue`
    """

    @staticmethod
    def from_yaml_file(filename: str, check_module_name: str = '') -> "ModuleManifest":
        """ Does the magic of import yaml to pydantic model"""
        with open(filename, 'r') as config_file:
            config = yaml.safe_load(config_file)
        manifest = ModuleManifest(**config['fastiot_module'])

        if check_module_name and manifest.name != check_module_name:
            raise ValueError(f'Error raised during parsing of file "{filename}": '
                             f'Module name in manifest file "{manifest.name}" differs from expected module '
                             f'name "{check_module_name}".')

        return manifest

    @classmethod
    def from_docker_image(cls, docker_image_name: str) -> "ModuleManifest":
        # The manifest file is always located inside the container and has the name '/opt/fastiot/manifest.yaml'.
        # We have to mount a volume and copy the file into the volume. If we mounted a file directly, we sometimes get
        # errors overwriting the file from inside the container. To avoid trouble, we mount a directory.

        # Some chars not suitable for docker but for shell commands, do some checking here
        dangerous_chars = [' ', ';', '&', '<', '>', '|']
        if True in [char in dangerous_chars for char in docker_image_name]:
            raise ValueError(f"Image name {docker_image_name} seems to be invalid. Aborting action.")

        with tempfile.TemporaryDirectory() as tempdir:
            tempfile_name = f"{tempdir}/manifest.yaml"
            export_cmd = f"docker run --rm {docker_image_name} cat /opt/fastiot/manifest.yaml > {tempfile_name}"
            get_cli_logger().info('Exporting manifest from docker image command: %s', export_cmd)
            ret = os.system(shlex_quote(export_cmd))
            if ret != 0:
                raise OSError(f"Could not read manifest.yaml file from docker image {docker_image_name}")

            return cls.from_yaml_file(filename=tempfile_name)
