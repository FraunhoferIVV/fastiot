import importlib
import logging
from typing import Optional, Dict

from fastiot.cli.configuration import external_services  # noqa  # pylint: disable=unused-import
from fastiot.cli.model import ProjectConfig, ExternalService


def get_services_list(project_config: Optional[ProjectConfig] = None) -> Dict[str, ExternalService]:
    """ Method to get a list of all available services as instantiated :class:fastiot.cli.model:FastIoTService`.

    To append own services you simply have to inherit from :class:fastiot.cli.model:FastIoTService` and put them into
    your project as `project.cli.services`. This method will try to import anything from there and for services.
    """
    if project_config is not None:
        for extension in project_config.extensions:
            try:
                importlib.import_module(f'{extension}.cli.services')
            except ImportError:  # Extension does not provide any services
                logging.debug("Could not import service under %s.cli.services from extension %s", extension, extension)

    service_classes = ExternalService.__subclasses__()
    services = [s() for s in service_classes]
    return {s.name: s for s in services}
