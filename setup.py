#!/usr/bin/env python3
import os
import pathlib
import sys
from typing import List

from setuptools import setup, find_packages

requirements_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'requirements.txt'))
if not os.path.isfile(requirements_file):
    raise RuntimeError("Could not find a requirements.txt")

install_requires = []
with open(requirements_file) as f:
    for req in f.read().splitlines():
        req = req.strip()
        if req != '' and not req.startswith('#'):
            install_requires.append(req)

# Include fastiot. Please note that we have to prevent __init__.py file inside fastiot from being executed because it
# would trigger package imports which may fail.
_python_src_dir = os.path.join(os.path.dirname(__file__), 'src', 'fastiot', 'cli')
if _python_src_dir not in sys.path:
    sys.path.append(_python_src_dir)

# See upper comment. Most likely your IDE will mark these imports as missing which you can ignore.
from constants import TEMPLATES_DIR  # noqa
from version import create_version_file, get_version  # noqa


create_version_file(destination='src/fastiot/__version__.py')


def get_package_data_for_templates() -> List[str]:
    files = pathlib.Path(TEMPLATES_DIR).rglob('*')
    files = [str(f) for f in files if os.path.isfile(f)]
    return files


package_data = get_package_data_for_templates()
package_data.append(requirements_file)

mongodb_deps = ["pymongo>=4.1,<5"]
mariadb_deps = ["PyMySQL>=1.0,<2"]
postgredb_deps = ["psycopg2>=2.9.3,<3"]
influxdb_deps = ["influxdb-client[async]>=1.32,<2"]
opcua_deps = ["opcua>=0.98.8,<1", "asyncua"]
dash_deps = ["dash~=2.6.1", "plotly~=5.9.0"]
fastapi_deps = ["fastapi", "aiofiles", "uvicorn[standard]"]
compile_deps = ["nuitka"]

setup(
    name='fastiot',
    version=get_version(complete=True),
    description='FastIoT Platform',
    author='Fraunhofer IVV',
    author_email='tilman.klaeger@ivv-dd.fraunhofer.de;konstantin.merker@ivv-dd.fraunhofer.de',
    url='https://redmine.ivv-dd.fhg.de/projects/fastiot',
    packages=find_packages("src", include=["fastiot", "fastiot.*"]),
    package_dir={"": "src"},
    package_data={"fastiot": package_data},
    scripts=['bin/fiot'],
    python_requires='~=3.8',
    install_requires=install_requires,
    extras_require={
        "mongodb": mongodb_deps,
        "mariadb": mariadb_deps,
        "postgredb": postgredb_deps,
        "influxdb": influxdb_deps,
        "opcua": opcua_deps,
        "dash": dash_deps,
        "fastapi": fastapi_deps,
        "compile": compile_deps,
        "all": [
            *mongodb_deps, *mariadb_deps, *postgredb_deps, *influxdb_deps, *opcua_deps, *dash_deps, *fastapi_deps,
            *compile_deps
        ]
    }
)
