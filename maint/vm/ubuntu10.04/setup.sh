#!/bin/sh

set -e

apt-get update

# The oddly-named python-software-properties includes add-apt-repository.
APT_PACKAGES="
python-pip
python-dev
python-software-properties
"

apt-get -y install $APT_PACKAGES

add-apt-repository ppa:fkrull/deadsnakes
apt-get update

DEADSNAKES_PACKAGES="
python2.5
python2.5-dev
python2.7
python2.7-dev
"

apt-get -y install $DEADSNAKES_PACKAGES

PIP_PACKAGES="
virtualenv
tox
"

pip install $PIP_PACKAGES

/plop/maint/vm/shared-setup.sh
