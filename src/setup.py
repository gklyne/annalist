#!/usr/bin/env python
#
# NOTE: when testing, use "pip install ... --upgrade"

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
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
          , 'annalist_root.oauth2'
          , 'annalist_root.miscutils'
        ],
    package_dir = 
        { 'annalist_root':  'annalist_root'
        # , 'annalist':       'annalist_root/annalist'
        # , 'annalist_site':  'annalist_root/annalist_site'
        # , 'utils':          'annalist_root/annalist'
        # , 'oauth2':         'annalist_root/utils'
        # , 'miscutils':      'annalist_root/miscutils'
        },
    # >>>> REMEMBER to also update MANIFEST.in ... <<<<
    package_data = 
        { 'annalist_root':
            [ '*.sh', '*.txt'
            # Pre-assembled data for tests; not used by running system
            , 'sampledata/README.md'
            , 'sampledata/testinit/annalist_site/*.md'
            , 'sampledata/testinit/annalist_site/*.jpg'
            , 'sampledata/testinit/annalist_site/_annalist_site/*.jsonld'
            , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/*.jsonld'
            , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/lists/*/*.jsonld'
            , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/types/*/*.jsonld'
            , 'sampledata/testinit/annalist_site/c/*/_annalist_collection/views/*/*.jsonld'
            , 'sampledata/testinit/annalist_site/c/*/d/*/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/*.md'
            , 'sampledata/bibtestinit/annalist_site/*.jpg'
            , 'sampledata/bibtestinit/annalist_site/_annalist_site/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/enums/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/enums/*/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/fields/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/groups/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/lists/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/types/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/_annalist_collection/views/*/*.jsonld'
            , 'sampledata/bibtestinit/annalist_site/c/*/d/*/*/*.jsonld'
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
            , 'data/sitedata/enums/*/*/*.jsonld'
            , 'data/sitedata/fields/*/*.jsonld'
            , 'data/sitedata/groups/*/*.jsonld'
            , 'data/sitedata/lists/*/*.jsonld'
            , 'data/sitedata/types/*/*.jsonld'
            , 'data/sitedata/views/*/*.jsonld'
            , 'data/sitedata/users/*/*.jsonld'
            , 'data/sitedata/vocabs/*/*.jsonld'
            , 'data/bibdata/enums/*/*/*.jsonld'
            , 'data/bibdata/fields/*/*.jsonld'
            , 'data/bibdata/groups/*/*.jsonld'
            , 'data/bibdata/lists/*/*.jsonld'
            , 'data/bibdata/types/*/*.jsonld'
            , 'data/bibdata/views/*/*.jsonld'
            , 'data/bibdata/vocabs/*/*.jsonld'
            , 'data/test/*.md'
            , 'data/test/*.jpg'
            ]
        , 'annalist_root.annalist.views':
            [ 'help/*.md'
            , 'help/*.html'
            ]
        , 'annalist_root.oauth2':
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
        , 'rdflib-jsonld==0.3'
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
