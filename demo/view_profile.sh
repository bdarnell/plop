#!/bin/bash

set -e
dir="$(dirname "${BASH_SOURCE[0]}")"

if [[ ! -f "$dir/envs/plop-demo/bin/activate" ]]; then
    ./setup.sh
fi
source "$dir/envs/plop-demo/bin/activate"

echo "Starting server, go to http://localhost:8888"
python -mplop.viewer --datadir=profiles
