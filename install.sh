#!/bin/bash

DIR_NAME=$(dirname $0)

if [ -z "$FASTIOT_EXTRA_PYPI" ]; then

python3 -m pip install --extra-index-url https://www.piwheels.org/simple/ \
    --no-cache-dir -r $DIR_NAME/requirements.txt

else

python3 -m pip install --extra-index-url https://www.piwheels.org/simple/ \
    --extra-index-url http://${FASTIOT_EXTRA_PYPI} --trusted-host ${FASTIOT_EXTRA_PYPI} \
    --no-cache-dir -r $DIR_NAME/requirements.txt

fi

