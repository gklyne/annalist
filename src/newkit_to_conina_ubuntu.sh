#!/usr/bin/env bash

ANNALIST_VER=$(annalist-manager version)

python setup.py build sdist
scp -i ~/.ssh/id_rsa_openstack_gk \
    dist/Annalist-${ANNALIST_VER}.tar.gz  annalist@conina-ubuntu:

