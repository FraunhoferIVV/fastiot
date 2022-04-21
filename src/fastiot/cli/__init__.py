"""
Methods and classes within this directory are mainly for setting up new projects and building exisiting ones
locally or with the Jenkins pipeline
"""
from fastiot.cli import version
from fastiot.cli.exceptions import ResolveError
from fastiot.cli.make_setup_fn import make_setup, find_modules, \
    CustomModuleConfig, ModulePackageConfig

try:
    from fastiot.cli.__version__ import __version__
except ImportError:
    __version__ = version.get_version(complete=True)
