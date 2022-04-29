from abc import ABC, abstractmethod
from typing import List, Any, Dict

from fastiot.cli.configuration.context import CliContext


class Command(ABC):
    @abstractmethod
    def execute(self, context: CliContext, vargs: List[str]):
        pass

    @abstractmethod
    def print_help(self, context: CliContext):
        pass
