#!/usr/bin/env bash

DIR_NAME=$(dirname $0)

python3 -m pip install --extra-index-url https://www.piwheels.org/simple/ \
    --extra-index-url http://${FASTIOT_EXTRA_PYPI} --trusted-host ${FASTIOT_EXTRA_PYPI} \
    --no-cache-dir -r $DIR_NAME/requirements.txt
