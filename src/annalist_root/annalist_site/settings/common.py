"""
Django settings for annalist_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import django
import sys
import string
import random
import logging
import logging.handlers
from annalist import __version__
from annalist import layout

DJANGO_ROOT     = os.path.dirname(os.path.realpath(django.__file__))
SETTINGS_DIR    = os.path.dirname(os.path.realpath(__file__))           # src/annalist_root/annalist_site/settings
SITE_CONFIG_DIR = os.path.dirname(SETTINGS_DIR)                         # src/annalist_root/annalist_site
SITE_SRC_ROOT   = os.path.dirname(SITE_CONFIG_DIR)                      # src/annalist_root
SAMPLEDATA_DIR  = SITE_SRC_ROOT+"/sampledata/data"                      # src/annalist_root/sampledata

ANNALIST_SITE_SEG = "annalist"              # Base URL path segment for Annalist site
ANNALIST_SITE_REF = ANNALIST_SITE_SEG+"/"   # Base URL path for Annalist site
ANNALIST_LOG_FILE = "annalist.log"
ACCESS_LOG_FILE   = "annalist-wsgi-access.log"
ERROR_LOG_FILE    = "annalist-wsgi-error.log"

class RotatingNewFileHandler(logging.handlers.RotatingFileHandler):
    """
    Define a rotating file logging handler that additionally forces a new file 
    the first time it is instantiated in a run of the containing program.

    NOTE: if multiple file handlers are used with in an application, only the
    first one instantiated will be allocated a new file at startup.  The
    class variable '_newfile' might be replaced with a dictionary
    indexed by the (fully expanded) filename.
    """

    _newfile = False

    def __init__(self, *args, **kwargs):
        super(RotatingNewFileHandler, self).__init__(*args, **kwargs)
        if not RotatingNewFileHandler._newfile:
            self.doRollover()
            RotatingNewFileHandler._newfile = True
        return

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Define secret key for various Django functions
# See: 
#   https://stackoverflow.com/a/15383766/324122
#   https://stackoverflow.com/a/23728630/324122
#
# SECURITY WARNING: keep the secret key used in production secret!
KEY_CHARS  = string.ascii_letters + string.digits + string.punctuation
SECRET_KEY = ''.join(
                random.SystemRandom().choice(KEY_CHARS) 
                for _ in range(32)
                )
# See also: https://stackoverflow.com/a/23728630/324122
# SECRET_KEY = '@-+h*%@h+0yj(^c9y-=1a@9l^@xzub200ofq2@a$gm2k_l*$pf'

# UPDATE: running under 'gunicorn', I've found that session logins get dumped
# periodcally when the worker process periodically restarts.  
# Hence I'm trying to find an alternative that attempts to be more "sticky", 
# without depending on a predefinbed secret key.
#
# Options I'm considering:
# (a) use an environment variable set randomly when starting the server,
# (b) use the file system to persist a randomly generated value
#
# Currently, I prefer the environment variable approach:
# For this to work, set the environment variable in 'annalist-manager' when 
# running under 'gunicorn'. If not defined, use randomly key (from above).

if "ANNALIST_KEY" in os.environ:
    SECRET_KEY = os.environ["ANNALIST_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
# (overrides in settings.devel and settings.runtests)
DEBUG = False

# Logging level used by selected log statements whose output may be useful
# for tracing field values displayed in Annalist edit/view forms.
# Suggested use is to raise level to logging.INFO when running a single named
# test, when trying to understand how values end up in a form.
TRACE_FIELD_VALUE   = logging.INFO

ALLOWED_HOSTS = []

ROOT_URLCONF = 'annalist_site.urls'

WSGI_APPLICATION = 'annalist_site.wsgi.application'

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

# Customize authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',    # default
    'login.OAuth2CheckBackend.OAuth2CheckBackend'
    )

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'annalist',
    'login',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            "templates"
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': False,
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# DATABASE_PATH = os.path.join(SAMPLEDATA_DIR, 'annalist_site/db.sqlite3')
# DATABASES     = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME':   DATABASE_PATH,
#     }
# }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATIC_SEG = 'static'
STATIC_URL = '/'+STATIC_SEG+"/"

STATICFILES_DIRS = (
    ("",       SITE_SRC_ROOT+"/annalist/data/static"),
    ("images", SITE_SRC_ROOT+"/annalist/data/identity_providers/images"),
)

ANNALIST_VERSION = __version__
ANNALIST_VERSION_MSG = "Annalist version %s (common configuration)"%(ANNALIST_VERSION)

# End.
