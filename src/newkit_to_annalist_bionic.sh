#!/usr/bin/env bash

python setup.py clean --all
python setup.py build sdist

echo "Copying: dist/Annalist-0.5.14.tar.gz  ->  annalist@test-bionic-annalist.oerc.ox.ac.uk:/home/annalist/software"
scp -i ~/.ssh/id_rsa_openstack_gk\
    dist/Annalist-0.5.14.tar.gz annalist@test-bionic-annalist.oerc.ox.ac.uk:/home/annalist/software

