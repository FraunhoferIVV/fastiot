""" Some helpers to write CLI tests """
import logging
import os
from typing import Optional

from fastiot.cli.infrastructure_service_fn import get_services_list
from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.context import get_default_context


def init_default_context(configure_filename: Optional[str] = None):
    """ Sets up the default context as it is usually done by the starting point of cli app """

    # We need to search for a configure file as running the tests as script will most likely be another working
    # directory as running them from e.g. PyCharm
    try:
        _ = os.getcwd()
    except FileNotFoundError:
        logging.warning(f"Most probably some other test changed the working directory to "
                        f"`{os.readlink('/proc/self/cwd')}` and did move back.\n This is a bad practice and you should "
                        f"find the test that’s using `os.chdir`. We will try change back to the project root dir.")
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
