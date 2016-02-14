#!/bin/bash

set -e
dir="$(dirname "${BASH_SOURCE[0]}")"
: ${PYTHON:=python}

if [[ ! -f "$dir/envs/plop-demo/bin/activate" ]]; then
    "$PYTHON" -mvenv "$dir/envs/plop-demo" || \
        "$PYTHON" -mvirtualenv --no-site-packages "$dir/envs/plop-demo"
fi
source "$dir/envs/plop-demo/bin/activate"

python -mpip install -r requirements.txt
