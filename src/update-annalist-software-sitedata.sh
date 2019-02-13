#!/usr/bin/env bash

echo "Update Annalist installed software and site data"
echo "(Assumes target Python virtualenv is already activated)"
echo ""

python setup.py clean --all
python setup.py build
pip uninstall -y annalist
python setup.py install
annalist-manager updatesite
annalist-manager collectstatic

#
# End.

