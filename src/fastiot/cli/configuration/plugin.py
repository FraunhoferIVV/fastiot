from typing import Dict

from fastiot.cli.configuration.command import Command


class Plugin:
    def __init__(self, commands: Dict[str, Command], services: Dict[str, Service]):
        self._commands = commands
        self._services = services

    @property
    def commands(self) -> Dict[str, Command]:
        return self._commands

    @property
    def services(self) -> Dict[str, Service]:
        return self._services

    @property
    def base_images(self) -> Dict[str]:
        pass
