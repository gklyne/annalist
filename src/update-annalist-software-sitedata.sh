#!/usr/bin/env bash

echo "Update Annalist installed software and site data"
echo "(Assumes target Python virtualenv is already activated)"
echo ""

python setup.py clean --all
pip uninstall -y annalist
pip install .
# python setup.py build
# python setup.py install
annalist-manager updatesite
annalist-manager collectstatic

#
# End.

