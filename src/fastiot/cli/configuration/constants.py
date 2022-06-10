import os

CONFIG_KEY_EXTENSIONS = "extensions"
DOCKER_BASE_IMAGE = "python:3.10-bullseye"  # Base image used to build docker files if not defined otherwise in manifest
CONFIGURE_FILE_NAME = "configure.py"

assets_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'common', 'assets')
