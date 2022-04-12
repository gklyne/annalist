#!/usr/bin/env bash

echo "Update Annalist installed software"
echo "(Assumes target Python virtualenv is already activated)"
echo ""

python setup.py clean --all
python setup.py build
python setup.py install

#
# End.

