#!/bin/bash

DIR_NAME=$(dirname $0)

PIP_EXTRA_ARGS=
if [ ! -z "$FASTIOT_EXTRA_PYPI" ]; then
PIP_EXTRA_ARGS="--extra-index-url http://${FASTIOT_EXTRA_PYPI} --trusted-host ${FASTIOT_EXTRA_PYPI}"
fi

find requirements -maxdepth 1 -name 'requirements*.txt' -print | xargs printf " -r %s" | xargs \
python3 -m pip install --extra-index-url https://www.piwheels.org/simple/ $PIP_EXTRA_ARGS --no-cache-dir
