"""
Annalist application
"""

__author__        = "Graham Klyne"
__author_email__  = "GK@ACM.ORG"
__copyright__     = "Copyright 2014, G. Klyne"
__license__       = "MIT (http://opensource.org/licenses/MIT)"

# https://docs.djangoproject.com/en/dev/ref/applications/
default_app_config = 'annalist.apps.AnnalistConfig'

"""
Software version number.

Even sub-releases are stable versions, except for critical bug-fixes
(designated by a patch letter at the end of the version string).

Odd sub-releases are work-in-progress, and may change from day-to-day.
"""
__version__        = "0.1.20"   # Software version number (odd = unstable)

"""
Data compatibility version: this is saved with collection data, and is used to
detect attempts to open newer data with older software.  It should be updated 
to the current version number whenever software updates would cause data to be
created that cannot be read by older versions of software.  (There is a general 
presumption that new software can read older data, and migrate it where necessary.)

Not all software updates create data that cannot be read by older software: for 
these updates the __version_data__ value can be left unchanged.
"""
__version_data__   = "0.1.20"   # Data compatibility version number

# End.
