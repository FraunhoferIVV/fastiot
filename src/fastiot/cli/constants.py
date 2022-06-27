import os

CONFIG_KEY_EXTENSIONS = "extensions"
DOCKER_BASE_IMAGE = "python:3.10-bullseye"  # Base image used to build docker files if not defined otherwise in manifest
CONFIGURE_FILE_NAME = "configure.py"
DEPLOYMENTS_CONFIG_DIR = 'deployments'
DEPLOYMENTS_CONFIG_FILE = 'deployment.yaml'
GENERATED_DEPLOYMENTS_DIR = 'generated'

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

FASTIOT_DOCKER_REGISTRY = 'FASTIOT_DOCKER_REGISTRY'
FASTIOT_DOCKER_REGISTRY_CACHE = 'FASTIOT_DOCKER_REGISTRY_CACHE'
