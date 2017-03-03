#!/usr/bin/env bash

python setup.py clean --all
python setup.py build sdist

echo "Copying: dist/Annalist-0.1.36.tar.gz  ->  graham@dev.annalist.net:/home/graham/software"
scp -i ~/.ssh/id_rsa-openstack-gklyne \
    dist/Annalist-0.1.36.tar.gz graham@dev.annalist.net:/home/graham/software

