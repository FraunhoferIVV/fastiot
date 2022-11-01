from typing import Dict
from pydantic import BaseModel

from fastiot.util.classproperty import classproperty


class DockerTemplate(BaseModel):
    name: str
    dir: str
    filename: str = 'Dockerfile.j2'

    @classproperty
    def all(cls) -> Dict[str, "DockerTemplate"]:
        """ Method to get a dict of all available services as instantiated
        :class:`fastiot.cli.model.infrastructure_service.InfrastructureService`.

        To append own services you simply have to inherit from this class and put them into your project. Then import
        those parts using :attr:`fastiot.cli.model.project.ProjectConfig.extensions`. This method will try to import
        anything from there and for services.
        """
        template_classes = DockerTemplate.__subclasses__()
        i_template_class = 0
        while i_template_class < len(template_classes):
            for subcls in template_classes[i_template_class].__subclasses__():
                if subcls not in template_classes:  # We have to check for multiple inheritance
                    template_classes.append(subcls)
            i_template_class += 1
        templates_list = [t() for t in template_classes]
        templates = {t.name: t for t in templates_list}
        return {k: templates[k] for k in sorted(templates.keys())}

    # we need this line for Pycharm IDE to detect type-hinting properly. Maybe it is fixed in the future
    all: Dict[str, "DockerTemplate"]

    @classmethod
    def get(cls, name: str) -> "DockerTemplate":
        template = cls.all.get(name)
        if template is None:
            raise ValueError(f"Template for name '{name}' not found. Please make sure to import it correctly.")
        return template
