""" Some helpers to write CLI tests """
import logging
import os

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model.project import ProjectContext
from fastiot.cli.typer_app import _import_infrastructure_services


def init_default_context(configure_filename: str = ''):
    """ Sets up the default context as it is usually done by the starting point of cli app """

    # We need to search for a configure file as running the tests as script will most likely be another working
    # directory as running them from e.g. PyCharm
    try:
        _ = os.getcwd()
    except FileNotFoundError:
        logging.warning("Most probably some other test changed the working directory to "
                        "%s and did move back.\n This is a bad practice and you should "
                        "find the test that’s using `os.chdir`. We will try change back to the project root dir.",
                        os.readlink('/proc/self/cwd'))
        os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

    if configure_filename is None:
        possible_filenames = ['configure.py', '../configure.py', '../../configure.py', '../../../configure.py']
        for filename in possible_filenames:
            if os.path.isfile(filename):
                configure_filename = filename
                break
    import_configure(ProjectContext.default, configure_filename)
    _import_infrastructure_services()

