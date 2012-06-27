#!/bin/sh

set -e

if [[ ! -f ~/envs/plop-demo/bin/activate ]]; then
    ./setup.sh
fi
source ~/envs/plop-demo/bin/activate

echo "Starting server, go to http://localhost:8888"
python -m plop.viewer --datadir=profiles
