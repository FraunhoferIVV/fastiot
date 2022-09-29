""" Data model for fastiot service manifests """
import os
import tempfile
from enum import Enum
from shlex import quote as shlex_quote
from typing import List, Dict, Optional

import yaml
from pydantic.main import BaseModel

from fastiot.cli.cli_logging import get_cli_logger
from fastiot.cli.constants import DEFAULT_BASE_IMAGE, MANIFEST_FILENAME


class Port(BaseModel):
    """
    A port entry represents one port used by the service which should be mounted outside the container.
    """

    port: int
    """
    The default port location.
    """
    env_variable: str
    """
    The environment variable which is passed to the container to change the port, e.g. for automated testing.
    """


class Volume(BaseModel):
    """
    A volume entry represents one directory used by the service which should be mounted outside the container.
    """

    location: str
    """
    The volume location to be used. If you provide something like :file:`/opt/mydata` it will be accessible as
    :file:`opt/mydata` in  your container.
    """
    env_variable: str
    """
    See attribute `env_variable` in :class:`fastiot.cli.model.manifest.Port`.
    """


class Device(BaseModel):
    """
    A device entry represents one device used by the service which should be mounted outside the container.
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
    no = "no"


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

    def as_qemu_platform(self):
        """ Returns the platform according the qemu emulator """
        if self == self.armv7:
            return 'arm'
        if self == 'amd64_2':
            return 'amd64'
        return self.value


class Healthcheck(str, Enum):
    """ TODO: Add some description here! """
    error_log = "error_log"


class Vue(BaseModel):
    """ Use this part if your project contains a frontend created with vue.js """

    src: str  # Source path relative to your application where the vue.js code is located
    dst: str  # Destination path where the build static files will be placed, e.g. 'static'
    configured_dist: str = 'dist'
    """
    Destination where vue.js will place its files for distribution. If not changed vue.js will have save its files
    in the `<vue-path>/dist` which is also the default here.
    If you have something like::

        service.exports = {
          outputDir:"../flask_server/static",
          assetsDir: "static"
        }


    in your :file:`vue.config.js` use the `outputDir` variable as relative path here.
    """


class ServiceManifest(BaseModel):
    """
    Every service needs a :file:`manifest.yaml` to describe the service.

    The following options may be used. The file always starts with a ``fastiot_service:`` in the first level. Then
    options from the following may (``name`` must) follow.

    :attr:`fastiot.cli.model.manifest.ServiceManifest.name` is needed, others are mostly optional!
    """
    name: str
    """ Name needs to comply with the services name (Mandatory) """
    ports: List[Port] = []
    """
    Provide a list with some name for the service and a port that this container will open, e.g. when operating
    as a webserver.`
    """
    base_image: str = DEFAULT_BASE_IMAGE
    """ Use this to provide an alternative base image, otherwise
    :const:`fastiot.cli.constants.DEFAULT_BASE_IMAGE` will be used.

    Be aware, that the further Dockerfile will be unchanged, thus your base image should be based on some Debian-style.
    If this does not work for you, you may also provide a :file:`Dockerfile` in your service which will automatically be
    used.
    """
    volumes: List[Volume] = []  # Volumes to be mounted in the container
    devices: List[Device] = []  # Devices, e.g. serial devices, to be mounted in the container
    depends_on: List[str] = []
    """
    List of infrastructure services that need to be deployed
    """
    mount_config_dir: MountConfigDirEnum = MountConfigDirEnum.optional
    privileged: bool = False
    """
    Enable if this service needs privileged permissions inside docker, e.g. for hardware access
    """
    platforms: List[CPUPlatform] = [CPUPlatform.amd64]
    """ Define the cpu platforms to build the container for. It defaults to amd64. If doing local builds the first one
    specified (or amd64 if none) will be used to build the image. """

    healthcheck: Optional[Healthcheck] = None  # Configure healthcheck for the container
    copy_dirs_to_container: List[str] = []
    """
    Directories which shall be copied to container. They must be specified relative to :file:`manifest.yaml`.
    """

    vue: Optional[Vue] = None
    """
    If your project contains a vue.js application you can automatically build it here. For required configuration
    see :class:`fastiot.cli.model.manifest.Vue`
    """

    additional_pip_packages: Optional[List[str]] = []
    """
    If one specific module needs more packages installed than the other you may add those here.

    **Caution**: It is recommended to use the projects global :file:`requirements.txt` to install additional packages
                 in your project. This way all packages will be installed at once and this container stage will later
                 be shared among all services of your project, so no additional space is needed. The major benefit is
                 to have all requirements being compatible with each other. Using this option here this cannot be
                 guaranteed.
    """

    @staticmethod
    def from_yaml_file(filename: str, check_service_name: str = '') -> "ServiceManifest":
        """ Does the magic of import yaml to pydantic model"""
        with open(filename, 'r') as config_file:
            config = yaml.safe_load(config_file)
        manifest = ServiceManifest(**config['fastiot_service'])

        if check_service_name and manifest.name != check_service_name:
            raise ValueError(f'Error raised during parsing of file "{filename}": '
                             f'service name in manifest file "{manifest.name}" differs from expected service '
                             f'name "{check_service_name}".')

        return manifest

    @classmethod
    def from_docker_image(cls, docker_image_name: str, pull_always: bool = False) -> "ServiceManifest":
        # The manifest file is always located inside the container and has the name '/opt/fastiot/manifest.yaml'.
        # We have to mount a volume and copy the file into the volume. If we mounted a file directly, we sometimes get
        # errors overwriting the file from inside the container. To avoid trouble, we mount a directory.

        # Some chars not suitable for docker but for shell commands, do some checking here
        dangerous_chars = [' ', ';', '&', '<', '>', '|']
        if True in [char in dangerous_chars for char in docker_image_name]:
            raise ValueError(f"Image name {docker_image_name} seems to be invalid. Aborting action.")

        if pull_always:
            cmd = f"docker pull {docker_image_name}"
            ret = os.system(shlex_quote(cmd))
            if ret != 0:
                raise OSError(f"Could not pull image {docker_image_name} from registry.")

        with tempfile.TemporaryDirectory() as tempdir:
            tempfile_name = f"{tempdir}/{MANIFEST_FILENAME}"
            export_cmd = f"docker run --rm {docker_image_name} cat /opt/fastiot/{MANIFEST_FILENAME} > {tempfile_name}"
            get_cli_logger().info('Exporting manifest from docker image command: %s', export_cmd)
            ret = os.system(shlex_quote(export_cmd))
            if ret != 0:
                raise OSError(f"Could not read manifest.yaml file from docker image {docker_image_name}")

            return cls.from_yaml_file(filename=tempfile_name)
