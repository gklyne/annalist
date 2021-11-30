#!/usr/bin/env bash

if [ "$1" == "" ]; then
     echo "Usage:"
     echo "  run test.sh <test-name>"
    exit
fi

# export DJANGO_SETTINGS_MODULE=annalist_site.settings.runtests
unset DJANGO_SETTINGS_MODULE
python manage.py test annalist.tests.$1
