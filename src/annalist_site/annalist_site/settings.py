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

# @@TODO: separate into common and enviroment-specific settins; 
#         cf. http://www.deploydjango.com/django_project_structure/

import os
import django
import sys

DJANGO_ROOT     = os.path.dirname(os.path.realpath(django.__file__))
SETTINGS_DIR    = os.path.dirname(os.path.realpath(__file__))
SITE_SRC_ROOT   = os.path.dirname(SETTINGS_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@-+h*%@h+0yj(^c9y-=1a@9l^@xzub200ofq2@a$gm2k_l*$pf'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

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
    'oauth2',
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
    'oauth2.OAuth2CheckBackend.OAuth2CheckBackend'
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

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    SITE_SRC_ROOT+"/static/",
    SITE_SRC_ROOT+"/annalist/static/",
)


# Directory to look for provider-specific client secrets and OAuth2 service details
CONFIG_BASE = "/etc/annalist/"
CONFIG_BASE = os.path.join(os.path.expanduser("~"), ".annalist/")

# Annalist configuration and metadata files
#
# Directory layout:
#
#   $BASE_DATA_DIR
#     annalist-site/
#       _annalist-site/
#         site_meta.json_ld
#       <collection-id>/
#         _annalist_collection/
#           coll_meta.jsonld
#           types/
#             <type-id>/
#               type_meta.jsonld
#              :
#           views/
#             <view-id>/
#               view_meta.jsonld
#              :
#           lists/
#             <list-id>/
#               list_meta.jsonld
#              :
#           bridges/
#             (bridge-description (incl path mapping in collection) - @@TBD)
#              :
#           user-groups/  @@TBD
#             group-description
#              :
#           access/  @@TBD
#             default-access
#             (more details to work through - keep it simple for starters)
#         <type-id>/
#           <entity-id>/
#             entity-data.jsonld
#             entity-prov.jsonld
#            :
#          :
#        :

# Pick one!
BASE_DATA_DIR  = "/var"
BASE_DATA_DIR  = os.path.expanduser("~")
BASE_DATA_DIR  = SITE_SRC_ROOT+"/test/data"

SITE_DIR       = "annalist_site"
SITE_PATH      = BASE_DATA_DIR + "/" + SITE_DIR
SITE_META_DIR  = "_annalist_site"
SITE_META_PATH = SITE_PATH + "/" + SITE_META_DIR
SITE_META_FILE = "site_meta.jsonld"

SITE_COLL_DIR  = "%(coll_id)s"
SITE_COLL_PATH = SITE_PATH + "/" + SITE_COLL_DIR

COLL_META_DIR  = "_annalist_collection"
COLL_META_PATH = SITE_COLL_PATH + "/" + COLL_META_DIR
COLL_META_FILE = "coll_meta.jsonld"

COLL_TYPE_DIR  = "types"
TYPE_META_DIR  = "%(type_id)s"
TYPE_META_PATH = SITE_COLL_PATH + "/" + COLL_TYPE_DIR + "/" + TYPE_META_DIR
TYPE_META_FILE = "type_meta.lsonld"

VIEW_META_DIR  = COLL_META_DIR + "/views"
VIEW_META_FILE = VIEW_META_DIR + "%(view_id)s/view_meta.lsonld"

LIST_META_DIR  = COLL_META_DIR + "/lists"
LIST_META_FILE = LIST_META_DIR + "%(list_id)s/list_meta.lsonld"

# and more...


# Log key path values

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
log.info("DJANGO_ROOT:    "+DJANGO_ROOT)
log.info("SETTINGS_DIR:   "+SETTINGS_DIR)
log.info("SITE_SRC_ROOT:  "+SITE_SRC_ROOT)
log.info("CONFIG_BASE:    "+CONFIG_BASE)
log.info("SITE_META_PATH: "+SITE_PATH)
log.info("DB PATH:        "+DATABASES['default']['NAME'])
log.debug("Python path:   "+repr(sys.path))

