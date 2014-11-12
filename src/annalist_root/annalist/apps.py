"""
Annalist application hooks
(cf. https://docs.djangoproject.com/en/dev/ref/applications/)

The main purpose of this is to log settings values to the loig file, 
after the log file configuration has been applied.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.conf import settings
from django.apps import AppConfig

import logging
log = logging.getLogger(__name__)

class AnnalistConfig(AppConfig):
    name = 'annalist'

    def ready(self):
        log.info(settings.ANNALIST_VERSION_MSG)
        log.info("SETTINGS_MODULE:  "+settings.SETTINGS_MODULE)
        log.info("BASE_DATA_DIR:    "+settings.BASE_DATA_DIR)
        log.info("CONFIG_BASE:      "+settings.CONFIG_BASE)
        log.info("DJANGO_ROOT:      "+settings.DJANGO_ROOT)
        log.info("SITE_CONFIG_DIR:  "+settings.SITE_CONFIG_DIR)
        log.info("SITE_SRC_ROOT:    "+settings.SITE_SRC_ROOT)
        log.info("STATICFILES_DIRS: "+settings.STATICFILES_DIRS[1])
        log.info("DB PATH:          "+settings.DATABASES['default']['NAME'])
        log.info("ALLOWED_HOSTS:    "+",".join(settings.ALLOWED_HOSTS))
        log.info("LOGGING_FILE:     "+settings.LOGGING_FILE)
        return

# End.
