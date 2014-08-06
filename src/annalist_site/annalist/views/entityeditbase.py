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
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap
from annalist.views.grouprepeatmap      import GroupRepeatMap

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

    def get_fields_entityvaluemap(self, collection, entityvaluemap, fields):
        # @@TODO: elide this
        entityvaluemap.append(
            FieldListValueMap(collection, fields)
            )
        return entityvaluemap
 
    # def find_repeat_fields(self, fieldmap=None):
    #     """
    #     Iterate over repeat field groups in the current view.

    #     Each value found is returned as a field structure description; e.g.

    #         { 'field_type': 'RepeatValuesMap'
    #         , 'repeat_entity_values': u 'annal:view_fields'
    #         , 'repeat_id': u 'View_fields'
    #         , 'repeat_btn_label': u 'field'
    #         , 'repeat_label': u 'Fields'
    #         , 'repeat_context_values': u 'repeat'
    #         , 'repeat_fields_description':
    #         , { 'field_type': 'FieldListValueMap'
    #           , 'field_list':
    #             [ { 'field_placement': Placement(field = u 'small-12 medium-6 columns', ... )
    #               , 'field_id': u 'Field_sel'
    #               }
    #             , { 'field_placement': Placement(field = u 'small-12 medium-6 columns', ... )
    #               , 'field_id': u 'Field_placement'
    #               }
    #             ]
    #           }
    #         }
    #     """
    #     def _find_repeat_fields(fieldmap):
    #         for kmap in fieldmap:
    #             field_desc = kmap.get_structure_description()
    #             if field_desc['field_type'] == "FieldListValueMap":
    #                 for fd in _find_repeat_fields(kmap.fs):
    #                     yield fd
    #             if field_desc['field_type'] == "RepeatValuesMap":
    #                 yield field_desc
    #     return _find_repeat_fields(self._entityvaluemap)

    # def find_add_field(self, form_data):
    #     """
    #     Locate add field option in form data and,if present, return a description of the field to
    #     be added.
    #     """
    #     for repeat_desc in self.find_repeat_fields():
    #         # log.info("find_add_field: %r"%repeat_desc)
    #         if repeat_desc['repeat_id']+"__add" in form_data:
    #             return repeat_desc
    #     return None

    # def find_remove_field(self, form_data):
    #     """
    #     Locate remove field option in form data and, if present, return a description of the field to
    #     be removed, with the list of member indexes to be removed added as element 'remove_fields'.
    #     """
    #     for repeat_desc in self.find_repeat_fields():
    #         # log.info("find_add_field: %r"%repeat_desc)
    #         if repeat_desc['repeat_id']+"__remove" in form_data:
    #             repeat_desc['remove_fields'] = form_data[repeat_desc['repeat_id']+"__select_fields"]
    #             return repeat_desc
    #     return None

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

    def map_form_data_to_values(self, form_data, **kwargs):
        log.debug("map_form_data_to_values: form_data %r"%(form_data))
        values = {}
        for kmap in self._entityvaluemap:
            values.update(kmap.map_form_to_entity(form_data))
        return values

# End.
