"""
Annalist view definitions and renderers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os

# Needed when importing django.views.generic - default to development settings
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'annalist_site.settings.devel'

__path__.append(os.path.join(os.path.dirname(__file__), "form_utils"))

# from annalist.views.form_utils import (
#     fielddescription,
#     entityvaluemap, fieldvaluemap,
#     fieldlistvaluemap, repeatvaluesmap, simplevaluemap
#     )

# End.
