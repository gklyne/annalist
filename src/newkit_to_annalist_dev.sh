#!/usr/bin/env bash

ANNALIST_VER=$(annalist-manager version)

python setup.py clean --all
python setup.py build sdist

echo "Copying: dist/Annalist-${ANNALIST_VER}.tar.gz  ->  graham@dev.annalist.net:/home/graham/software"
scp -i ~/.ssh/id_rsa-openstack-gklyne \
    dist/Annalist-${ANNALIST_VER}.tar.gz graham@dev.annalist.net:/home/graham/software

