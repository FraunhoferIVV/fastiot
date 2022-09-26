import os
from typing import Dict

from pydantic import BaseModel

from fastiot.cli.constants import FASTIOT_CONFIGURE_FILE
from fastiot.cli.import_configure import import_configure
from fastiot.cli.infrastructure_service_fn import get_services_list
from fastiot.cli.model import ProjectConfig, InfrastructureService


class Context(BaseModel):
    """
    Singleton class to hold the current context with e.g. project configuration
    """

    project_config: ProjectConfig = ProjectConfig()
    external_services: Dict[str, InfrastructureService] = {}


__default_context = None


def get_default_context() -> Context:
    """
    Use this method to retrieve the singleton :class:`fastiot.cli.model.context.Context`
    """
    global __default_context
    if __default_context is None:
        __default_context = Context()
        import_configure(
            project_config=__default_context.project_config,
            file_name=os.environ.get(FASTIOT_CONFIGURE_FILE, '')
        )
        __default_context.external_services = get_services_list()
    return __default_context
