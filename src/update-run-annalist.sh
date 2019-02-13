#!/usr/bin/env bash

echo "Assumes annalist environment has been activated, and latest software installed"
echo "e.g."
echo "    source anenv/bin/activate"
echo "    pip install /var/www/software/Annalist-0.1.xx.tar.gz --upgrade"
echo "    annalist-manager runtests"
echo ""

# Stop dev server instances, if any:
# killall python
# killall python2
# killall python3

annalist-manager stopserver   --personal
annalist-manager initialize   --personal
annalist-manager updatesite   --personal
annalist-manager collectsatic --personal
annalist-manager runserver    --personal

# This alternative runs the development server rather than gunicorn
# nohup annalist-manager rundevserver --personal >annalist.out &

# End.
