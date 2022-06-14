from abc import ABC, abstractmethod
from typing import List

from fastiot.cli.configuration.context import Context
from fastiot.cli.configuration.plugin_component import PluginComponent


class Command(PluginComponent, ABC):
    @abstractmethod
    def execute(self, context: Context, vargs: List[str]):
        pass

    @abstractmethod
    def print_help(self, context: Context):
        pass
