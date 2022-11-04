from fastiot.cli.constants import TEMPLATES_DIR
from fastiot.cli.model.docker_template import DockerTemplate


class PythonDockerTemplate(DockerTemplate):
    name = 'python3'
    dir = TEMPLATES_DIR
