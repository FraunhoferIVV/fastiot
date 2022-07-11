from typing import List, Dict

from pydantic.main import BaseModel


class ServiceComposeInfo(BaseModel):
    name: str
    image: str
    environment: Dict[str, str]
    ports: List[str]
    volumes: List[str]
