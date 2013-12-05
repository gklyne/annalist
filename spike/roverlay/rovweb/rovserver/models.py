
__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.db import models

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
