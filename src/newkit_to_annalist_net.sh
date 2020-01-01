#!/usr/bin/env bash

python setup.py clean --all
python setup.py build sdist

ANNALIST_VER=$(annalist-manager version)

echo "Copying: dist/Annalist-${ANNALIST_VER}.tar.gz  ->  annalist@annalist.net:/var/www/software"
scp -i ~/.ssh/id_rsa_openstack_gk \
    dist/Annalist-${ANNALIST_VER}.tar.gz annalist@annalist.net:/var/www/software

echo "Copying: ../documents/pages  ->  annalist@annalist.net:uploads"
scp -i ~/.ssh/id_rsa_openstack_gk \
    -r ../documents/pages annalist@annalist.net:uploads

echo "Copying ../documents/tutorial  ->  annalist@annalist.net:uploads/documents"
rm ../documents/tutorial/.DS_Store
scp -i ~/.ssh/id_rsa_openstack_gk \
    -r ../documents/tutorial annalist@annalist.net:uploads/documents

