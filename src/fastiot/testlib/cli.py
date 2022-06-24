""" Some helpers to write CLI tests """
import os
from typing import Optional

from fastiot.cli.external_service_helper import get_services_list
from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.context import get_default_context


def init_default_context(configure_filename: Optional[str] = None):
    """ Sets up the default context as it is usually done by the starting point of cli app """

    # We need to search for a configure file as running the tests as script will most likely be another working
    # directory as running them from e.g. PyCharm
    try:
        _ = os.getcwd()
    except FileNotFoundError:
        # This is some nasty workaround as it is unclear at the moment why, when running tests, os.getcwd() may fail.
        # This is working ok when running one testfile but not when running all of them :-/
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

    if configure_filename is None:
        possible_filenames = ['configure.py', '../configure.py', '../../configure.py', '../../../configure.py']
        for filename in possible_filenames:
            if os.path.isfile(filename):
                configure_filename = filename
                break
    default_context = get_default_context()
    default_context.project_config = import_configure(configure_filename)
    default_context.external_services = get_services_list()
