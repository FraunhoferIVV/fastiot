#! /usr/bin/python3
# -*- coding: utf-8 -*-
# Author: Douglas Creager <dcreager@dcreager.net> with additions by Fraunhofer IVV, DD
# This file is placed into the public domain.
# Calculates the current version number.  If possible, this is the
# output of “git describe”, modified to conform to the versioning
# scheme that setuptools uses.  If “git describe” returns an error
# (most likely because we're in an unpacked copy of a release tarball,
# rather than in a git working copy), then we fall back on reading the
# contents of the RELEASE-VERSION file.
#
# To use this script, simply import it your setup.py file, and use the
# results of get_git_version() as your package version:
#
# from version import *
#
# setup(
#     version=get_git_version(),
#     .
#     .
#     .
# )
#
#
# This will automatically update the RELEASE-VERSION file, if
# necessary.  Note that the RELEASE-VERSION file should *not* be
# checked into git; please add it to your top-level .gitignore file.
#
# You'll probably want to distribute the RELEASE-VERSION file in your
# sdist tarballs; to do this, just create a MANIFEST.in file that
# contains the following line:
#
#   include RELEASE-VERSION

import argparse
import logging
import os
import pathlib
import re
from subprocess import Popen, PIPE
from typing import Optional

GIT_UNSPECIFIED = "git-unspecified"


def _get_number_of_commits() -> int:
    with Popen(['git', 'rev-list', 'HEAD', '--count'], stdout=PIPE, stderr=PIPE) as p:
        return int(p.stdout.readlines()[0].decode('ascii').strip())


def _call_git_describe() -> Optional[str]:
    with Popen(['git', 'describe', '--abbrev=7', '--tag'], stdout=PIPE, stderr=PIPE) as p:
        result = p.stdout.readlines()
        if not result:
            return None
        else:
            return result[0].decode('ascii').strip()


def _call_git_branch() -> str:
    with Popen(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], stdout=PIPE, stderr=PIPE) as p:
        return p.stdout.readlines()[0].decode('ascii').strip()


def _git_version() -> str:

    try:
        branch = _call_git_branch()
    except IndexError:  # If git could not run (git not found, no git directory) readline[0] will fail with IndexError
        return GIT_UNSPECIFIED

    if branch == 'HEAD':
        branch = os.environ.get('GIT_BRANCH', 'main')

    for c in ['/', '-', '_']:  # Replace common separators by those accepted in PEP 440
        branch = branch.replace(c, '.')

    if not branch:  # if we have subtracted all chars, just name the branch unknown
        branch = 'unknown'

    # First try to get the current version using “git describe”.
    git_tag = _call_git_describe()

    if git_tag:
        # Match "[major].[minor]-[commits since tag as patch]" where the latest part "-[...]" is optional. Also a char
        # 'v' is optional at the beginning.
        match = re.search(r"^v?(\d+)\.(\d+)(?:-(\d+)-g[\w\d]+)?$", git_tag)
        if match:
            major = match.group(1)
            minor = match.group(2)
            patch = match.group(3)
            if not patch:
                patch = '0'
            patch = int(patch)
        else:
            raise ValueError(f"Invalid version tag '{git_tag}'.")

    else:
        logging.warning("No git tag has been set. Tag for version 0.0 is assumed and version 0.0.x will be created"
                        " for any following commits. Specify tag, e.g. 0.1, to remove this warning.")
        major = 0
        minor = 0
        patch = _get_number_of_commits()

    version = f"{major}.{minor}"
    if branch == 'master' or branch == 'main':
        if patch > 0:
            version += f'.{patch}'
    else:
        version += f'.dev{patch}+{branch}'

    # Finally, return the current version.
    return version


def _version_file_version() -> Optional[str]:

    def get_file():
        for root, dirs, files in os.walk(os.getcwd()):
            if "__version__.py" in files:
                return os.path.join(root, "__version__.py")

    file = get_file()
    if file is None:
        return None  # We did not find anything better
    try:
        with open(file).read() as file_contents:
            regex = r"__version__ ?= ?[\"\'](.*)[\"\']"
            version = re.search(regex, file_contents, re.MULTILINE)[1]
            return version
    except:  # Could not open file or find a suiting match
        return None


def create_version_file(destination: Optional[str] = None):
    """
    Creates a file with __version__=…

    :param destination: Destination to put the generated file. If not specified the file will be created in path above
    this version.py
    """

    version = get_version(complete=True)
    file_contents = f"__version__ = '{version}'\n"
    file_path = destination or os.path.abspath(
        os.path.join(pathlib.Path(__file__).parent.absolute(), '..', '__version__.py'))

    # Don’t overwrite anything that might be better than 'git_unspecified'
    if not (version == GIT_UNSPECIFIED and os.path.isfile(file_path)):
        with open(file_path, "w") as f:
            f.write(file_contents)


def get_version(complete=False, only_major=False, minor=False) -> str:
    """
    Returns the current version depending on the git commits and tags or version file

    :param complete: Set to true to get the full version including dev, e.g. 1.4+dev10
    :param only_major: Set to true to get only the major version, e.g. 1.x
    :param minor: Set to true to only get the minor version, e.g. .4
    :return: String with version
    """

    assert complete + only_major + minor <= 1, "Only one option for version output can be selected"

    if not (complete or only_major or minor):  # Nothing was selected
        complete = True  # Set some useful default

    version = _git_version()
    if version == GIT_UNSPECIFIED:
        version = _version_file_version() or version

    if complete:
        return version
    if only_major:
        return version.split('.')[0]
    if minor:
        parts = version.split('.')
        return f"{parts[0]}.{parts[1]}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Shows current version depending on git commits and tags")
    parser.add_argument('--complete', default=False, type=bool, required=False,
                        help="Show complete version string starting (Used if nothing else is specified)")
    parser.add_argument('--only_major', default=False, type=bool, required=False,
                        help="Show only the major version as number")
    parser.add_argument('--minor', default=False, type=bool, required=False,
                        help="Show major.minor version")
    args = vars(parser.parse_args())

    print(get_version(**args))
