import importlib
import logging
from typing import Dict, Union, Optional, List

from pydantic import BaseModel

from fastiot.cli.model import ProjectConfig


class ExternalService(BaseModel):
    """ Class to describe external services to be integrated in the deployments. """
    name: str  # Name of the external service, e.g. mariadb. Per convention these names should be in lower case
    docker_image: str  # Name of the docker image to be put in the :file:`docker-compose.yaml`
    port: int  # Default port of the service exposed by its docker image
    port_env_var: str
    """ Environment variable to read the port number, as for internal purposes the port number may change """
    additional_env: Optional[Dict[str, Union[str, int]]] = None
    """ Provide any additional environment variables to be set here as a dictionary with the variable name and a 
    sensible default. """
