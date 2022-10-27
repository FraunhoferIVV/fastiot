#!/usr/bin/env python3
from glob import glob
import os
import pathlib
import sys
from typing import List

from setuptools import setup, find_packages


requirement_files = glob("requirements*.txt", root_dir=os.path.join(os.path.dirname(__file__), 'requirements'))
requirement_files_abs = [os.path.join(os.path.dirname(__file__), 'requirements', f) for f in requirement_files]
install_requires = []
extras_require = {'all': []}

for req_name, req_name_abs in zip(requirement_files, requirement_files_abs):
    req_list = []
    with open(req_name_abs) as f:
        for req in f.read().splitlines():
            req = req.strip()
            if req != '' and not req.startswith('#'):
                req_list.append(req)
    if req_name == 'requirements.txt':
        install_requires.extend(req_list)
    else:
        middle_name = req_name.removeprefix('requirements.').removesuffix('.txt')
        extras_require[middle_name] = req_list
    extras_require['all'].extend(req_list)


if not install_requires:
    raise RuntimeError("Could not find a requirements.txt")


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
package_data.extend(requirement_files_abs)

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
    extras_require=extras_require
)
