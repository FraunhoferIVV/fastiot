from abc import ABC, abstractmethod


class PluginComponent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
