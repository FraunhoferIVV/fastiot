from typing import Dict, Any, List, Optional

from fastiot.cli.constants import CONFIG_KEY_EXTENSIONS
from fastiot.cli.model import ProjectConfig


class Context:
    def __init__(self):
        self.project_config: Optional[ProjectConfig] = None


__default_context = None


def get_default_context() -> Context:
    global __default_context
    if __default_context is None:
        __default_context = Context()
    return __default_context
