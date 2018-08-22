#!/usr/bin/env python
"""
Django application manager for Annalist
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

import os
import sys

# ----
# Install `faulthandler` and enable the next two lines to get stack trace
# diagnostic from segment fault error.
# ----
# import faulthandler
# faulthandler.enable()
# ----

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
