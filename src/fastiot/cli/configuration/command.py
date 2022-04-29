from abc import ABC, abstractmethod
from typing import List, Any, Dict

from fastiot.cli.configuration.context import Context


class Command(ABC):
    @abstractmethod
    def execute(self, context: Context, vargs: List[str]):
        pass

    @abstractmethod
    def print_help(self, context: Context):
        pass
