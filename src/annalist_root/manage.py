#!/usr/bin/env python

import os
import sys

if __name__ == "__main__":

    # Select default settings module
    #
    # To specify an alternative:
    #   python manage.py runserver --settings=annalist_site.settings.personal
    # or
    #   export DJANGO_SETTINGS_MODULE=annalist_site.settings.personal

    if 'test' in sys.argv:
        default_settings = "annalist_site.settings.runtests"
    else:
        default_settings = "annalist_site.settings.devel"

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

# End.
