
__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.db import models

from django.contrib.auth.models import User

from oauth2client.django_orm import FlowField
from oauth2client.django_orm import CredentialsField

# Create your models here.

class ResearchObject(models.Model):
    uri = models.URLField(max_length=1000)

    def __unicode__(self):
        return self.uri

class AggregatedResource(models.Model):
    ro     = models.ForeignKey("ResearchObject")
    uri    = models.URLField(max_length=1000)
    is_rdf = models.BooleanField()

    def __unicode__(self):
        return "%s (%s)"%(self.uri, self.is_rdf)

# See: https://developers.google.com/api-client-library/python/guide/django

# class FlowModel(models.Model):
#   id = models.ForeignKey(User, primary_key=True)
#   flow = FlowField()

class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()
