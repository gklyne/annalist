#!/usr/bin/env python
#
# NOTE: when testing, use "pip install ... --upgrade"

# from __future__ import unicode_literals # (import Fails under Pythons)
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# Setup.py based on https://github.com/paltman/python-setup-template/blob/master/setup.py,
# following http://www.ibm.com/developerworks/opensource/library/os-pythonpackaging/index.html
#
# These could be useful:
#   https://wiki.python.org/moin/Distutils/Tutorial
#   https://pypi.python.org/pypi/check-manifest

import codecs
import os
import sys

from distutils.util import convert_path
from fnmatch import fnmatchcase
from setuptools import setup, find_packages

if sys.version_info[:2] not in [(2,7),(3,6),(3,7)]:
    raise AssertionError("Annalist requires Python 2.7 or 3.6 (found Python %s.%s)"%sys.version_info[:2])

dir_here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dir_here, "annalist_root"))

# Helper to load README.rst, etc.
def read(fname):
    return codecs.open(os.path.join(dir_here, fname)).read()

PACKAGE         = "annalist"
PACKAGE_MODULE  = __import__(PACKAGE, globals(), locals(), ['__version__', '__author__'])
VERSION         = PACKAGE_MODULE.__version__
AUTHOR          = PACKAGE_MODULE.__author__
AUTHOR_EMAIL    = "gk-pypi@ninebynine.org"
NAME            = "Annalist"
DESCRIPTION     = "Annalist linked data notebook"
URL             = "https://github.com/gklyne/annalist"

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = read("README.rst"),
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    license = "MIT",
    url = URL,
    packages = 
        [ 'annalist_root'
          , 'annalist_root.annalist'
            , 'annalist_root.annalist.models'
            , 'annalist_root.annalist.views'
            , 'annalist_root.annalist.views.fields'
            , 'annalist_root.annalist.views.form_utils'
            , 'annalist_root.annalist.tests'
          , 'annalist_root.annalist_site'
            , 'annalist_root.annalist_site.settings'
          , 'annalist_root.annalist_manager'
          , 'annalist_root.annalist_manager.tests'
          , 'annalist_root.utils'
          , 'annalist_root.login'
          , 'annalist_root.miscutils'
        ],
    package_dir = 
        { 'annalist_root':  'annalist_root'
        },
    # >>>> REMEMBER to also update MANIFEST.in ... <<<<
    package_data = 
        { 'annalist_root':
            [ '*.sh', '*.txt'
            # Pre-assembled data for tests; not used by running system
            , 'sampledata/README.md'
            , 'sampledata/testinit/annalist_test/*.md'
            , 'sampledata/testinit/annalist_test/*.jpg'
            , 'sampledata/testinit/annalist_test/*.jsonld'
            , 'sampledata/testinit/annalist_test/c/*/d/*.jsonld'
            , 'sampledata/testinit/annalist_test/c/*/d/*/*/*.jsonld'
            ]
        , 'annalist_root.annalist':
            [ 'templates/*.html'
            , 'templates/field/*.html'
            , 'data/static/css/*.css'
            , 'data/static/js/*.js'
            , 'data/static/images/*.png'
            , 'data/static/images/icons/warning_32.png'
            , 'data/static/images/icons/search_32.png'
            , 'data/static/foundation/css/*.css'
            , 'data/static/foundation/js/foundation/*.js'
            , 'data/static/foundation/js/vendor/*.js'
            # Indentity provider data
            , 'data/identity_providers/*.md'
            , 'data/identity_providers/*.json'
            , 'data/identity_providers/*.example'
            , 'data/identity_providers/images/*.png'
            , 'data/identity_providers/images/*.jpg'
            , 'data/identity_providers/images/*.svg'
            # Configuration example data
            , 'data/config_examples/*'
            # Site-wide data definitions
            , 'data/sitedata/_enum_field_placement/*/*.jsonld'
            , 'data/sitedata/_enum_list_type/*/*.jsonld'
            , 'data/sitedata/_enum_render_type/*/*.jsonld'
            , 'data/sitedata/_enum_value_mode/*/*.jsonld'
            , 'data/sitedata/_enum_value_type/*/*.jsonld'
            , 'data/sitedata/_field/*/*.jsonld'
            #@@ , 'data/sitedata/_group/*/*.jsonld'
            , 'data/sitedata/_list/*/*.jsonld'
            , 'data/sitedata/_type/*/*.jsonld'
            , 'data/sitedata/_view/*/*.jsonld'
            , 'data/sitedata/_user/*/*.jsonld'
            , 'data/sitedata/_vocab/*/*.jsonld'
            , 'data/sitedata/_info/*/*.jsonld'
            # Bibliographic data definitions
            , 'data/Bibliography_defs/_field/*/*.jsonld'
            , 'data/Bibliography_defs/_group/*/*.jsonld'
            , 'data/Bibliography_defs/_list/*/*.jsonld'
            , 'data/Bibliography_defs/_type/*/*.jsonld'
            , 'data/Bibliography_defs/_view/*/*.jsonld'
            , 'data/Bibliography_defs/_vocab/*/*.jsonld'
            , 'data/Bibliography_defs/entitydata/*/*.jsonld'
            , 'data/Bibliography_defs/entitydata/*/*/*.jsonld'
            , 'data/Bibliography_defs/entitydata/*/*/*/*.jsonld'
            # Vocabulary namespace definitions
            , 'data/namedata/_field/*/*.jsonld'
            , 'data/namedata/_group/*/*.jsonld'
            , 'data/namedata/_list/*/*.jsonld'
            , 'data/namedata/_type/*/*.jsonld'
            , 'data/namedata/_view/*/*.jsonld'
            , 'data/namedata/_vocab/*/*.jsonld'
            # Resource definitions
            , 'data/Resource_defs/_field/*/*.jsonld'
            , 'data/Resource_defs/_group/*/*.jsonld'
            , 'data/Resource_defs/_list/*/*.jsonld'
            , 'data/Resource_defs/_type/*/*.jsonld'
            , 'data/Resource_defs/_view/*/*.jsonld'
            , 'data/Resource_defs/_vocab/*/*.jsonld'
            , 'data/Resource_defs/entitydata/*/*.jsonld'
            , 'data/Resource_defs/entitydata/*/*/*.jsonld'
            , 'data/Resource_defs/entitydata/*/*/*/*.jsonld'
            # Concept definitions
            , 'data/Concept_defs/_field/*/*.jsonld'
            , 'data/Concept_defs/_group/*/*.jsonld'
            , 'data/Concept_defs/_list/*/*.jsonld'
            , 'data/Concept_defs/_type/*/*.jsonld'
            , 'data/Concept_defs/_view/*/*.jsonld'
            , 'data/Concept_defs/_vocab/*/*.jsonld'
            , 'data/Concept_defs/entitydata/*/*.jsonld'
            , 'data/Concept_defs/entitydata/*/*/*.jsonld'
            , 'data/Concept_defs/entitydata/*/*/*/*.jsonld'
            # Journal definitions
            , 'data/Journal_defs/_field/*/*.jsonld'
            , 'data/Journal_defs/_group/*/*.jsonld'
            , 'data/Journal_defs/_list/*/*.jsonld'
            , 'data/Journal_defs/_type/*/*.jsonld'
            , 'data/Journal_defs/_view/*/*.jsonld'
            , 'data/Journal_defs/_vocab/*/*.jsonld'
            , 'data/Journal_defs/entitydata/*/*.jsonld'
            , 'data/Journal_defs/entitydata/*/*/*.jsonld'
            , 'data/Journal_defs/entitydata/*/*/*/*.jsonld'
            # RDF schema definitions
            , 'data/RDF_schema_defs/_field/*/*.jsonld'
            , 'data/RDF_schema_defs/_group/*/*.jsonld'
            , 'data/RDF_schema_defs/_list/*/*.jsonld'
            , 'data/RDF_schema_defs/_type/*/*.jsonld'
            , 'data/RDF_schema_defs/_view/*/*.jsonld'
            # Annalist schema
            , 'data/Annalist_schema/entitydata/*/*.jsonld'
            , 'data/Annalist_schema/entitydata/*/*/*.jsonld'
            , 'data/Annalist_schema/entitydata/*/*/*/*.jsonld'
            # Test data
            , 'data/test/*.md'
            , 'data/test/*.jpg'
            ]
        , 'annalist_root.annalist.views':
            [ 'help/*.md'
            , 'help/*.html'
            ]
        , 'annalist_root.login':
            [ 'templates/*.html'
            ]
        },
    exclude_package_data = {
        '': ['spike/*'] 
        },
    data_files = 
        [
        ],
    classifiers=
        [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        ],
    zip_safe = False,
    install_requires =
        [ 'Django==1.11.20'
        , 'six==1.11.0'
        , 'futures==3.2.0'
        , 'requests==2.20.0'
          , 'urllib3==1.24.2'
          , 'chardet==3.0.4'
          , 'idna==2.6'
          , 'requests-oauthlib==0.8.0'
          , 'oauthlib==2.0.7'
          , 'certifi==2018.1.18'
          , 'httplib2==0.11.3'
        , 'rdflib==4.2.2'
          , 'isodate==0.6.0'
          , 'rdflib-jsonld==0.4.0'
        , 'pyparsing==2.2.0'
        , 'Markdown==2.6.11'
        # For deployment
        , 'gunicorn==19.9.0'
        # For testing:
        , 'httpretty==0.9.4'
        , 'beautifulsoup4==4.6.0'
        ],
    entry_points =
        {
        'console_scripts':
            [ 'annalist-manager = annalist_root.annalist_manager.am_main:runMain',
            ]
        }
    )

if sys.version_info[:2] >= (3,7):
    print("*****")
    print("Warning: Django 1.11 does not work with Python versions after 3.6")
    print("See: https://docs.djangoproject.com/en/2.1/faq/install/#what-python-version-can-i-use-with-django")
    print("     https://stackoverflow.com/a/48822656/324122")

# End.
