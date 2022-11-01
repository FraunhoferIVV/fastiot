""" Data model for configurations of fastIoT based projects """

from fastiot.cli.model.deployment import ServiceConfig, InfrastructureServiceConfig, DeploymentConfig, \
    DeploymentTargetSetup, AnsibleHost
from fastiot.cli.model.manifest import ServiceManifest, CPUPlatform, Device, Healthcheck, MountConfigDirEnum, Port, \
    Volume, NPM
from fastiot.cli.model.project import CompileSettingsEnum, ProjectContext
from fastiot.cli.model.service import Service
from fastiot.cli.model.infrastructure_service import InfrastructureService
from fastiot.cli.model.docker_template import DockerTemplate
