#!/bin/bash

rm -rf docs/source/api
mkdir -p docs/source/api/fastiot_sample_services
mkdir -p docs/source/api/fastiot_core_services
mkdir -p docs/source/api/fastiot

export SPHINX_APIDOC_OPTIONS='members'


sphinx-apidoc --module-first --ext-autodoc --ext-coverage --ext-todo -d 1 -o "docs/source/api/fastiot_sample_services" "src/fastiot_sample_services"
sphinx-apidoc --module-first --ext-autodoc --ext-coverage --ext-todo -d 1 --separate -o "docs/source/api/fastiot_core_services" "src/fastiot_core_services"
sphinx-apidoc --module-first --ext-autodoc --ext-coverage --ext-todo -d 1 --separate -o "docs/source/api/fastiot" "src/fastiot"
