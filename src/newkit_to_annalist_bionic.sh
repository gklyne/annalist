#!/usr/bin/env bash

ANNALIST_VER=$(annalist-manager version)

python setup.py clean --all
python setup.py build sdist

echo "Copying: dist/Annalist-${ANNALIST_VER}.tar.gz  ->  annalist@test-bionic-annalist.oerc.ox.ac.uk:/home/annalist/software"
scp -i ~/.ssh/id_rsa_openstack_gk\
    dist/Annalist-${ANNALIST_VER}.tar.gz annalist@test-bionic-annalist.oerc.ox.ac.uk:/home/annalist/software

