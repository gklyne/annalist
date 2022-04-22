#!/usr/bin/env bash

echo "Reinstall Annalist software from current source tree"
echo ""

pip uninstall annalist
pip install .
# python setup.py clean --all
# python setup.py build
# python setup.py install
annalist-manager runtests

# End.
