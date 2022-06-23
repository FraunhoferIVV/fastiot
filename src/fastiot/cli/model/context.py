from typing import List, Optional

from fastiot.cli.model import ProjectConfig, ExternalService


class Context:
    """ Singleton class to hold the current context with e.g. project configuration """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.project_config: Optional[ProjectConfig] = None
        self.external_services: Optional[List[ExternalService]] = None


__default_context = None


def get_default_context() -> Context:
    """ Use this method to retrieve the singleton :class:`fastiot.cli.model.context.Context` """
    global __default_context
    if __default_context is None:
        __default_context = Context()
    return __default_context
