#!/usr/bin/env bash

ANNALIST_VER=$(annalist-manager version)

python setup.py clean --all
python setup.py build sdist

echo "Copying: dist/Annalist-${ANNALIST_VER}.tar.gz  ->  graham@dev.annalist.net:/home/graham/uploads/"
scp -i ~/.ssh/id_rsa_annalist-net.annalist-dev \
    dist/Annalist-${ANNALIST_VER}.tar.gz annalist-dev@dev.annalist.net:/home/annalist-dev/uploads/

