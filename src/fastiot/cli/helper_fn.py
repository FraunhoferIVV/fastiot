import logging
import os
from glob import glob
from typing import Dict, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def get_cli_logger():
    return logging.getLogger("fastiot.cli")


def parse_env_file(env_filename: str) -> Dict[str, str]:
    environment = {}
    with open(env_filename, 'r') as stream:
        for i_line, line in enumerate(stream.readlines()):
            # need a space before '#' or e.g. password containing # will be split
            i_comment = line.find(' #')
            if i_comment != -1:
                line = line[0:i_comment]
            line = line.strip()
            if line == '' or line[0] == '#':
                continue
            parts = line.split('=', maxsplit=2)
            parts = [p.strip() for p in parts]
            if len(parts) == 1 or parts[0].replace("_", "").isalnum() is False:
                raise ValueError(f"Cannot parse env file: Invalid line {i_line + 1}: {line}")
            environment[parts[0]] = parts[1]
    return environment


def get_jinja_env(search_path):
    jinja_env = Environment(
        loader=FileSystemLoader(search_path),
        trim_blocks=True,
        undefined=StrictUndefined
    )
    return jinja_env


def find_modules(package_name: str, project_root_dir: str):
    package_dir = os.path.join(project_root_dir, 'src', package_name)
    return [os.path.basename(m) for m in glob(package_dir + "/*") if os.path.isfile(os.path.join(m, 'manifest.yaml'))]
