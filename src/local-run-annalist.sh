#!/usr/bin/env bash

echo "Run Annalist for local HTTP access"

echo "Assumes annalist environment has been activated, and latest software installed"
echo "e.g."
echo "    source anenv/bin/activate"
echo "    pip install /var/www/software/Annalist-0.1.xx.tar.gz --upgrade"
echo "    annalist-manager runtests"
echo ""

killall python
killall python2
killall python3
OAUTHLIB_INSECURE_TRANSPORT=1 annalist-manager runserver --personal

# End.
