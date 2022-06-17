from fastiot.cli.version import get_version

try:
    from fastiot.__version__ import __version__
except ImportError:
    __version__ = get_version(complete=True)
