#!/usr/bin/env python
#
# NOTE: when testing, use "pip install ... --upgrade"

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
from pip.req import parse_requirements      # See: http://stackoverflow.com/questions/14399534/

if sys.version_info[:2] != (2,7):
    raise AssertionError("Annalist requires Python 2.7 (found Python %s.%s)"%sys.version_info[:2])

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
            , 'sampledata/testinit/annalist_site/*.md'
            , 'sampledata/testinit/annalist_site/*.jpg'
            # , 'sampledata/testinit/annalist_site/_annalist_site/*.jsonld'
            , 'sampledata/testinit/annalist_site/c/*/d/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_enum_field_placement/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_enum_list_type/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_enum_render_type/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_enum_value_mode/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_enum_value_type/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_field/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_group/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_list/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_type/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_user/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_view/*/*.jsonld'
            # , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/_vocab/*/*.jsonld'
            , 'sampledata/testinit/annalist_site/c/*/d/*/*/*.jsonld'
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
            # Site-wide data definitions
            , 'data/sitedata/_enum_field_placement/*/*.jsonld'
            , 'data/sitedata/_enum_list_type/*/*.jsonld'
            , 'data/sitedata/_enum_render_type/*/*.jsonld'
            , 'data/sitedata/_enum_value_mode/*/*.jsonld'
            , 'data/sitedata/_enum_value_type/*/*.jsonld'
            , 'data/sitedata/_field/*/*.jsonld'
            , 'data/sitedata/_group/*/*.jsonld'
            , 'data/sitedata/_list/*/*.jsonld'
            , 'data/sitedata/_type/*/*.jsonld'
            , 'data/sitedata/_view/*/*.jsonld'
            , 'data/sitedata/_user/*/*.jsonld'
            , 'data/sitedata/_vocab/*/*.jsonld'
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
            # RDF schema definitions
            , 'data/RDF_schema_defs/_field/*/*.jsonld'
            , 'data/RDF_schema_defs/_group/*/*.jsonld'
            , 'data/RDF_schema_defs/_list/*/*.jsonld'
            , 'data/RDF_schema_defs/_type/*/*.jsonld'
            , 'data/RDF_schema_defs/_view/*/*.jsonld'
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
    zip_safe = False,
    install_requires =
        [ 'Django==1.7'
          , 'wsgiref==0.1.2'
        , 'oauth2client==1.2'
          , 'httplib2==0.9'
        , 'pyparsing==2.0.2'
        , 'Markdown==2.5.2'
        # For testing:
        , 'httpretty==0.8.10'
        , 'beautifulsoup4==4.4.0'
          , 'html5lib==1.0b8'
        , 'rdflib==4.2.1'
        # , 'rdflib-jsonld==0.3'
        , 'rdflib-jsonld==0.4.0'
          , 'SPARQLWrapper==1.6.4'
          , 'isodate==0.5.1'
          , 'wsgiref==0.1.2'
          , 'six==1.10.0'
        ],
    entry_points =
        {
        'console_scripts':
            [ 'annalist-manager = annalist_root.annalist_manager.am_main:runMain',
            ]
        }
    )

# End.
