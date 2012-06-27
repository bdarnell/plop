#!/bin/sh

set -e

if [[ ! -f ~/envs/plop-demo/bin/activate ]]; then
    ./setup.sh
fi
source ~/envs/plop-demo/bin/activate

python -m busy_server &
server_pid=$!

# let the server start up
sleep 1

mkdir -p profiles
curl http://localhost:8888/_profile > profiles/profile.out

kill $server_pid
