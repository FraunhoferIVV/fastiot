from typing import Dict, Any, List

from fastiot.cli.configuration.constants import CONFIG_KEY_EXTENSIONS


class Context:
    def __init__(self, config: Dict[str, Any]):
        self._config: Dict[str, Any] = {}

    @property
    def extensions(self) -> List[str]:
        if CONFIG_KEY_EXTENSIONS in self._config:
            return self._config[CONFIG_KEY_EXTENSIONS]
        else:
            return []

    @property
    def module_names(self):
        pass

    @property
    def config(self) -> Dict[str, Any]:
        pass
