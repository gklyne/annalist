"""
OAuth2 / OpenID Connect authentication related models
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.db import models
from django.contrib.auth.models import User

from oauth2client.django_orm import Storage, CredentialsField

# See: https://developers.google.com/api-client-library/python/guide/django
class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()

def get_user_credential(userid):
    storage = Storage(CredentialsModel, 'id', userid, 'credential')
    return storage.get()

# End.