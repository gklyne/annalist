#!/usr/bin/env bash
#
# Regenerate installed system sitedata from source tree sitedata.
#
# Reinstalls the software, runs the "updatesite" option.
# The steps here are designed to ensure that all old installed site data is removed.
#
# Run this script from the `src` directory.
#

echo "Regenerate installed system sitedata from source tree sitedata."
echo "Run this script from the `src` directory."

python setup.py clean --all
python setup.py build
pip uninstall -y annalist
python setup.py install
annalist-manager updatesite

echo "To start server with updated site data: annalist-manager runserver"
