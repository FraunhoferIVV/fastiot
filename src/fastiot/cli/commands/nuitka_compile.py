import importlib
import logging
import os.path
import subprocess
import sys
from importlib.util import find_spec

import typer

from fastiot.cli.typer_app import app


@app.command()
def nuitka_compile(package_name: str = typer.Argument(default=None, help='The package to compile, e.g. `fastiot`'),
                   src_dir: str = typer.Option(default='src', help="The location of source files",
                                               exists=True, file_okay=False),
                   out_dir: str = typer.Option(default='output',
                                               help="The location for output files. It is relative to src_dir"),
                   install_nuitka: bool = typer.Option(default=False, help="Will try to install Nuitka using pip.")):
    """
    Compiles the selected path as .so file using nuitka. Please make sure to have Nuitka installed as this is an
    optional dependency.
    """
    if install_nuitka:
        logging.info("Trying to install Nuitka for you, please be patient!")
        exit_code = subprocess.call("/usr/bin/env python3 -m pip install -U nuitka".split(), cwd=src_dir)
        if exit_code != 0:
            logging.warning("Failed to install Nuitka!")

    try:
        importlib.import_module("nuitka")
    except ImportError:
        raise RuntimeError("You have to install the package nuitka manually using `pip install nuitka` for this command"
                           " to be working or try using the option `--install-nuitka`")

    if package_name is None:
        raise NameError("No package_name set.")

    if not os.path.isdir(os.path.join(src_dir, package_name)):
        raise FileNotFoundError(
            f"The `{package_name}` could not be found in the specified source directory `{src_dir}`!")

    recommended_packages = []
    all_packages = [package_name]
    all_packages += [p for p in recommended_packages if find_spec(p) is not None]

    nuitka_options = f"--python-flag=no_site --remove-output --no-pyi-file --output-dir={out_dir} --lto=yes --module"
    recurses = " ".join(["--include-package=" + x for x in all_packages])

    nuitka_cmd = f"/usr/bin/env python3 -m nuitka {nuitka_options} {recurses} {package_name}"

    logging.info(nuitka_cmd)
    exit_code = subprocess.call(f"{nuitka_cmd}".split(), cwd=src_dir)
    sys.exit(exit_code)
