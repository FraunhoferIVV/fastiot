#!/bin/bash

source ../venv/bin/activate

rm -rf source/api
mkdir -p source/api/mods
mkdir -p source/api/lib

sphinx-apidoc --module-first --ext-autodoc --ext-coverage -o source/api/mods ../src/fastiot_core_services
sphinx-apidoc --module-first --ext-autodoc --ext-coverage -o source/api/lib ../src/fastiot_sample_services


make html
