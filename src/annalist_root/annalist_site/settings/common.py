"""
Django settings for annalist_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import django
import sys
import logging
import logging.handlers
from annalist import __version__
from annalist import layout

DJANGO_ROOT     = os.path.dirname(os.path.realpath(django.__file__))
SETTINGS_DIR    = os.path.dirname(os.path.realpath(__file__))           # src/annalist_root/annalist_site/settings
SITE_CONFIG_DIR = os.path.dirname(SETTINGS_DIR)                         # src/annalist_root/annalist_site
SITE_SRC_ROOT   = os.path.dirname(SITE_CONFIG_DIR)                      # src/annalist_root
SAMPLEDATA_DIR  = SITE_SRC_ROOT+"/sampledata"                           # src/annalist_root/sampledata

class RotatingNewFileHandler(logging.handlers.RotatingFileHandler):
    """
    Define a rotating file logging handler that additionally forces a new file 
    the first time it is instantiated in a run of the containing program.

    NOTE: if multiple file hanfdlers are used with in an application, only the
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

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@-+h*%@h+0yj(^c9y-=1a@9l^@xzub200ofq2@a$gm2k_l*$pf'

# SECURITY WARNING: don't run with debug turned on in production!
# (overrides in settings.devel and settings.runtests)
DEBUG = False
TEMPLATE_DEBUG = False

# Logging level used by selected log statements whose output may be useful
# for tracing field values displayed in Annalist edit/view forms.
# Suggested use is to raise level to logging.INFO when running a single named
# test, when trying to understand how values end up in a form.
TRACE_FIELD_VALUE   = logging.INFO

ALLOWED_HOSTS = []

# Application definition

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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'annalist_site.urls'

WSGI_APPLICATION = 'annalist_site.wsgi.application'

# Customize authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',    # default
    'login.OAuth2CheckBackend.OAuth2CheckBackend'
    )

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SITE_SRC_ROOT, 'db.sqlite3'),
    }
}

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

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    # SITE_SRC_ROOT+"/static/",
    SITE_SRC_ROOT+"/annalist/data/static/",
    SITE_SRC_ROOT+"/annalist/data/identity_providers/",
)

ANNALIST_VERSION = __version__
ANNALIST_VERSION_MSG = "Annalist version %s (common configuration)"%(ANNALIST_VERSION)

# End.
