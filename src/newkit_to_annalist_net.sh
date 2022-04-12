#!/usr/bin/env bash
#
# Run from src/ directory

ANNALIST_VER=$(annalist-manager version)

python setup.py clean --all
python setup.py build sdist

echo "Copying: dist/Annalist-${ANNALIST_VER}.tar.gz  ->  annalist@annalist.net:/home/annalist/uploads"
scp -i ~/.ssh/id_rsa_annalist-net.annalist \
    dist/Annalist-${ANNALIST_VER}.tar.gz annalist@annalist.net:uploads/

echo "Copying: ../documents/pages  ->  annalist@annalist.net:uploads"
scp -i ~/.ssh/id_rsa_annalist-net.annalist \
    -r ../documents/pages annalist@annalist.net:uploads/pages/

echo "Copying ../documents/tutorial  ->  annalist@annalist.net:uploads/documents"
rm ../documents/tutorial/.DS_Store
scp -i ~/.ssh/id_rsa_annalist-net.annalist \
    -r ../documents/tutorial annalist@annalist.net:uploads/tutorial/

echo "Copying ../scripts  ->  annalist@annalist.net:uploads/scripts"
rm ../scripts/.DS_Store
scp -i ~/.ssh/id_rsa_annalist-net.annalist \
    -r ../scripts annalist@annalist.net:uploads/scripts/
