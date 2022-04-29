from typing import Dict, Any


class CliContext:
    def __init__(self, config: Dict[str, Any]):
        self._config: Dict[str, Any] = {}

    @property
    def module_names(self):
        pass

    @property
    def config(self) -> Dict[str, Any]:
        pass
