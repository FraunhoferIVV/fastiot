#!/bin/bash

source ../venv/bin/activate

rm -rf source/api
mkdir -p source/api/fastiot_sample_services
mkdir -p source/api/fastiot_core_services
mkdir -p source/api/fastiot

export SPHINX_APIDOC_OPTIONS='members'
EXTENSIONS="--module-first --ext-autodoc --ext-coverage --ext-todo"

sphinx-apidoc ${EXTENSIONS} -o source/api/fastiot_sample_services ../src/fastiot_sample_services
sphinx-apidoc ${EXTENSIONS} --separate -o source/api/fastiot_core_services ../src/fastiot_core_services
sphinx-apidoc ${EXTENSIONS} -o source/api/fastiot ../src/fastiot


make html
