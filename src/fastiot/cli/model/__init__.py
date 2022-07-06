""" Data model for configurations of fastIoT based projects """

from fastiot.cli.model.deployment import ServiceConfig, InfrastructureServiceConfig, DeploymentConfig, \
    DeploymentTargetSetup, AnsibleHost
from fastiot.cli.model.manifest import ServiceManifest, CPUPlatform, Device, Healthcheck, MountConfigDirEnum, Port, \
    Volume, Vue
from fastiot.cli.model.project import CompileSettingsEnum, ProjectConfig
from fastiot.cli.model.service import Service, InfrastructureService
