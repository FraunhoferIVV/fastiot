#!/bin/bash

source venv/bin/activate

docs/prepare_docs.sh


cd docs && make html
