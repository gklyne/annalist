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

from annalist.models.site               import Site
from annalist.models.sitedata           import SiteData
from annalist.models.collection         import Collection
from annalist.models.recordview         import RecordView
from annalist.models.recordlist         import RecordList
from annalist.models.recordfield        import RecordField
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData

from annalist.views.uri_builder         import uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.repeatdescription   import RepeatDescription
from annalist.views.generic             import AnnalistGenericView
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap
from annalist.views.grouprepeatmap      import GroupRepeatMap

from annalist.fields.render_utils       import bound_field, get_placement_classes
from annalist.fields.render_utils       import get_edit_renderer, get_view_renderer
from annalist.fields.render_utils       import get_head_renderer, get_item_renderer

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
 
    def find_repeat_fields(self, fieldmap=None):
        """
        Iterate over repeat field groups in the current view.

        Each value found is returned as a field structure description; e.g.

            { 'field_type': 'RepeatValuesMap'
            , 'repeat_entity_values': u 'annal:view_fields'
            , 'repeat_id': u 'View_fields'
            , 'repeat_btn_label': u 'field'
            , 'repeat_label': u 'Fields'
            , 'repeat_context_values': u 'repeat'
            , 'repeat_fields_description':
            , { 'field_type': 'FieldListValueMap'
              , 'field_list':
                [ { 'field_placement': Placement(field = u 'small-12 medium-6 columns', ... )
                  , 'field_id': u 'Field_sel'
                  }
                , { 'field_placement': Placement(field = u 'small-12 medium-6 columns', ... )
                  , 'field_id': u 'Field_placement'
                  }
                ]
              }
            }
        """
        def _find_repeat_fields(fieldmap):
            for kmap in fieldmap:
                field_desc = kmap.get_structure_description()
                if field_desc['field_type'] == "FieldListValueMap":
                    for fd in _find_repeat_fields(kmap.fs):
                        yield fd
                if field_desc['field_type'] == "RepeatValuesMap":
                    yield field_desc
        return _find_repeat_fields(self._entityvaluemap)

    def find_add_field(self, form_data):
        """
        Locate add field option in form data and,if present, return a description of the field to
        be added.
        """
        for repeat_desc in self.find_repeat_fields():
            # log.info("find_add_field: %r"%repeat_desc)
            if repeat_desc['repeat_id']+"__add" in form_data:
                return repeat_desc
        return None

    def find_remove_field(self, form_data):
        """
        Locate remove field option in form data and, if present, return a description of the field to
        be removed, with the list of member indexes to be removed added as element 'remove_fields'.
        """
        for repeat_desc in self.find_repeat_fields():
            # log.info("find_add_field: %r"%repeat_desc)
            if repeat_desc['repeat_id']+"__remove" in form_data:
                repeat_desc['remove_fields'] = form_data[repeat_desc['repeat_id']+"__select_fields"]
                return repeat_desc
        return None

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


#   -------------------------------------------------------------------------------------------
#
#   Generic delete entity confirmation response handling class
#
#   -------------------------------------------------------------------------------------------

# @@TODO: move this class to a separate module

class EntityDeleteConfirmedBaseView(AnnalistGenericView):
    """
    View class to perform completion of confirmed entity deletion, requested
    from collection edit view.
    """
    def __init__(self):
        super(EntityDeleteConfirmedBaseView, self).__init__()
        return

    def complete_remove_entity(self, coll_id, type_id, entity_id, continuation_uri):
        """
        Complete action to remove an entity.
        """
        viewinfo = DisplayInfo(self)
        viewinfo.get_site_info(self.get_request_host())
        viewinfo.get_coll_info(coll_id)
        viewinfo.get_type_info(type_id)
        viewinfo.check_authorization("delete")
        if viewinfo.http_response:
            return viewinfo.http_response
        typeinfo     = viewinfo.entitytypeinfo
        message_vals = {'id': entity_id, 'type_id': type_id, 'coll_id': coll_id}
        messages     = (
            { 'entity_removed': typeinfo.entitymessages['entity_removed']%message_vals
            })
        err = typeinfo.entityclass.remove(typeinfo.entityparent, entity_id)
        if err:
            return self.redirect_error(continuation_uri, str(err))
        return self.redirect_info(continuation_uri, messages['entity_removed'])

    # def confirm_form_respose(self, request, entity_id, remove_fn, messages, continuation_uri):
    #     """
    #     Process options to complete action to remove an entity
    #     """
    #     # @@TODO consider eliding this class 
    #     err     = remove_fn(entity_id)
    #     if err:
    #         return self.redirect_error(continuation_uri, str(err))
    #     return self.redirect_info(continuation_uri, messages['entity_removed'])

# End.
