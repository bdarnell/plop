#!/bin/bash

set -e

if [[ ! -f ~/envs/plop-demo/bin/activate ]]; then
    virtualenv -p python2.7 --no-site-packages ~/envs/plop-demo
fi
source ~/envs/plop-demo/bin/activate

pip install -r requirements.txt
