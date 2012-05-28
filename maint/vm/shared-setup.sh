#!/bin/sh
# Run at the end of each vm's provisioning script

set -e

# Link tox.ini into the home directory so you can run tox immediately
# after ssh'ing in.
ln -sf /vagrant/tox.ini ~vagrant/tox.ini
