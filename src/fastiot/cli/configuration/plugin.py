from typing import List

from fastiot.cli.configuration.command import Command
from fastiot.cli.configuration.image_template import ImageTemplate
from fastiot.cli.configuration.service import Service


class Plugin:
    def __init__(self,
                 commands: List[Command] = None,
                 services: List[Service] = None,
                 image_templates: List[ImageTemplate] = None):
        self._commands = commands if commands is not None else []
        self._services = services if services is not None else []
        self._image_templates = image_templates if image_templates is not None else []

    @property
    def commands(self) -> List[Command]:
        return self._commands

    @property
    def services(self) -> List[Service]:
        return self._services

    @property
    def image_templates(self) -> List[ImageTemplate]:
        return self._image_templates
