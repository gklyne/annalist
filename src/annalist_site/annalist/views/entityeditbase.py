"""
Annalist base classes for record editing views and form response handlers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import copy
import collections

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect
from django.core.urlresolvers           import resolve, reverse

from annalist                           import layout
from annalist                           import message
from annalist.exceptions                import Annalist_Error
from annalist.identifiers               import RDF, RDFS, ANNAL
from annalist                           import util

from annalist.views.uri_builder         import uri_with_params
from annalist.views.repeatdescription   import RepeatDescription
from annalist.views.generic             import AnnalistGenericView
# from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
# from annalist.views.grouprepeatmap      import GroupRepeatMap

#   -------------------------------------------------------------------------------------------
#
#   Generic view base class (contains methods common to record lists and views)
#
#   -------------------------------------------------------------------------------------------

class EntityEditBaseView(AnnalistGenericView):
    """
    View class base for handling entity edits (new, copy, edit, delete logic)

    This class contains shared logic, and must be subclassed to provide specific
    details for an entity type.
    """
    def __init__(self):
        super(EntityEditBaseView, self).__init__()
        return

    def map_value_to_context(self, entity_values, **kwargs):
        """
        Map data from entity values to view context for rendering.

        Values defined in the supplied entity take priority, and the keyword arguments provide
        values when the entity does not.
        """
        context = {}
        for kmap in self._entityvaluemap:
            context.update(kmap.map_entity_to_context(entity_values, extras=kwargs))
        return context

    def map_form_data_to_values(self, form_data, **kwargs):
        log.debug("map_form_data_to_values: form_data %r"%(form_data))
        values = {}
        for kmap in self._entityvaluemap:
            values.update(kmap.map_form_to_entity(form_data))
        return values

    def map_form_data_to_context(self, form_data, **kwargs):
        """
        Map values from form data to view context for form re-rendering.

        Values defined in the supplied form data take priority, and the keyword arguments provide
        values where the form data does not.
        """
        # log.info("\n*********\nmap_form_data_to_context: form_data: %r"%form_data)
        entityvals = self.map_form_data_to_values(form_data)
        # log.info("\n*********\nmap_form_data_to_context: entityvals: %r"%entityvals)
        context = self.map_value_to_context(entityvals, **kwargs)
        # log.info("\n*********\nmap_form_data_to_context: context: %r"%context)
        # log.info("\n*********")
        return context

# End.
