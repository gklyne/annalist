"""
Default record view/edit
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import copy

import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from annalist                       import layout
from annalist                       import message
# from annalist.exceptions            import Annalist_Error
# from annalist.identifiers           import RDF, RDFS, ANNAL
# from annalist                       import util

# from annalist.models.site           import Site
from annalist.models.sitedata       import SiteData
from annalist.models.collection     import Collection
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.entitydata     import EntityData

# from annalist.views.generic         import AnnalistGenericView
from annalist.views.entityeditbase  import EntityEditBaseView # , EntityDeleteConfirmedBaseView
from annalist.views.entityeditbase  import EntityValueMap
from annalist.fields.render_utils   import get_renderer, get_placement_class

class EntityDefaultEditView(EntityEditBaseView):
    """
    View class for default record edit view
    """

    # These values are referenced via instances, so can also be generated dynamically per-instance...
    _entityformtemplate = 'annalist_entity_edit.html'
    _entityclass        = None          # to be supplied dynamically
    _entityvaluemap     = (             # to be supplied dynamically, based on this:
        # Special fields
        [ EntityValueMap(e=None,          v=None,           c='title',            f=None               )
        , EntityValueMap(e=None,          v=None,           c='coll_id',          f=None               )
        , EntityValueMap(e=None,          v=None,           c='type_id',          f=None               )
        , EntityValueMap(e=None,          v='annal:id',     c='entity_id',        f='entity_id'        )
        , EntityValueMap(e='annal:uri',   v='annal:uri',    c='entity_uri',       f='entity_uri'       )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        , EntityValueMap(e=None,          v=None,           c='orig_entity_id',   f='orig_entity_id'   )
        , EntityValueMap(e=None,          v=None,           c='continuation_uri', f='continuation_uri' )
        , EntityValueMap(e=None,          v=None,           c='action',           f='action'           )
        ])

    def __init__(self):
        super(EntityDefaultEditView, self).__init__()
        self._entityclass    = None
        # self._entityvaluemap = None
        return

    # Support

    def get_coll_type_data(self, coll_id, type_id):
        """
        Check collection and type identifiers, and set up objects for:
            self.collection
            self.recordtype
            self.recordtypedata
            self._entityclass

        Returns None if all is well, or an HttpResponse object with details 
        about any problem encountered.
        """
        self.sitedata = SiteData(self.site(), layout.SITEDATA_DIR)
        # Check collection
        if not Collection.exists(self.site(), coll_id):
            return self.error(
                dict(self.error404values(), 
                    message=message.COLLECTION_NOT_EXISTS%(coll_id)
                    )
                )
        self.collection = Collection(self.site(), coll_id)
        # Check type
        if not RecordType.exists(self.collection, type_id):
            return self.error(
                dict(self.error404values(),
                    message=message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)
                    )
                )
        self.recordtype     = RecordType(self.collection, type_id)
        self.recordtypedata = RecordTypeData(self.collection, type_id)
        self._entityclass   = EntityData
        return None

    def get_form_entityvaluemap(self, view_id):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions.
        """
        # Locate and read view description
        # view_id      = "Default_view"
        entitymap  = EntityDefaultEditView._entityvaluemap.copy()
        entityview = RecordView.load(self.collection, view_id)
        log.debug("entityview   %r"%entityview.get_values())
        # Process fields referenced by the view desription, updating value map
        for f in entityview.get_values()['annal:view_fields']:
            field_id   = f['annal:field_id']
            viewfield  = RecordField.load(self.collection, field_id)
            log.debug("viewfield   %r"%(viewfield and viewfield.get_values()))
            return_property_uri = (
                viewfield['annal:property_uri'] if viewfield['annal:return_value'] 
                else None
                )
            field_context = (
                { 'field_id':           field_id
                , 'field_placement':    get_placement_class(f['annal:field_placement'])
                , 'field_name':         field_id    # Assumes same field can't repeat in form
                , 'field_render':       get_renderer(viewfield['annal:field_render'])
                , 'field_label':        viewfield['rdfs:label']
                , 'field_help':         viewfield['rdfs:comment']
                , 'field_value_type':   viewfield['annal:value_type']
                , 'field_placeholder':  viewfield['annal:placeholder']
                # 'field_value':        field value to be supplied
                })
            entitymap.append(
                EntityValueMap(
                    v=viewfield['annal:property_uri'],  # Entity value used to initialize context
                    c="field_value",                    # Key for value in (sub)context
                    s=("fields", field_context),        # Field sub-context
                    f=field_id,                         # Field name in form
                    e=return_property_uri               # Entity value returned from form
                    )
                )
        self._entityvaluemap = entitymap
        return entitymap


    # GET

    def get(self, request, coll_id=None, type_id=None, entity_id=None, action=None):
        """
        Create a form for editing an entity.
        """
        log.info("defaultedit.get: coll_id %s, type_id %s, entity_id %s, action %s"%
            (coll_id, type_id, entity_id, action)
            )
        http_response = (
            self.get_coll_type_data(coll_id, type_id) or
            self.form_edit_auth(action, self.recordtypedata._entityuri)
            )
        if http_response:
            return http_response
        # Set up RecordType-specific values
        entity_id  = self.get_entityid(action, self.recordtypedata, entity_id)
        # Create local entity object or load values from existing
        entity_initial_values  = (
            { "rdfs:label":   "Record '%s' of type '%s' in collection '%s'"%(entity_id, type_id, coll_id)
            , "rdfs:comment": ""
            })
        entity = self.get_entity(action, self.recordtypedata, entity_id, entity_initial_values)
        if entity is None:
            return self.error(
                dict(self.error404values(),
                    message=message.DOES_NOT_EXIST%(entity_initial_values['rdfs:label'])
                    )
                )
        # Set up initial view context
        # view_id     = "Default_view"
        # self.get_form_entityvaluemap()
        viewcontext = self.map_value_to_context(entity,
            title               = self.site_data()["title"],
            continuation_uri    = request.GET.get('continuation_uri', None),
            heading             = entity_initial_values['rdfs:label'],
            action              = action,
            coll_id             = coll_id,
            type_id             = type_id,
            orig_entity_id      = entity_id
            )
        viewcontext['fields'] = []
        # Locate and read view description
        # @@TODO: error recovery for missing vierws/fields
        view_id     = "Default_view"
        entityview   = RecordView.load(self.collection, view_id, altparent=self.sitedata)
        entityvalues = entity.get_values()
        log.debug("entityvalues %r"%entityvalues)
        log.debug("entityview   %r"%entityview.get_values())
        # Process fields referenced by the view desription, updating value map and
        for f in entityview.get_values()['annal:view_fields']:
            field_id   = f['annal:field_id']             
            viewfield  = RecordField.load(self.collection, field_id, altparent=self.sitedata)
            log.debug("viewfield   %r"%(viewfield and viewfield.get_values()))
            fieldvalue = entityvalues[viewfield['annal:property_uri']]
            field_context = (
                { 'field_id':           field_id
                , 'field_placement':    get_placement_class(f['annal:field_placement'])
                , 'field_name':         field_id    # Assumes same field can't repeat in form
                , 'field_render':       get_renderer(viewfield['annal:field_render'])
                , 'field_label':        viewfield['rdfs:label']
                , 'field_help':         viewfield['rdfs:comment']
                , 'field_value_type':   viewfield['annal:value_type']
                , 'field_placeholder':  viewfield['annal:placeholder']
                , 'field_property_uri': viewfield['annal:property_uri']
                , 'field_value':        fieldvalue
                })
            viewcontext['fields'].append(field_context)
        # generate and return form data
        return (
            self.render_html(viewcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id=None, type_id=None, entity_id=None, action=None):
        """
        Handle response from dynamically generatred entity editing form.
        """
        log.debug("views.defaultedit.post %s"%(self.get_request_path()))
        # log.info("  coll_id %s, type_id %s, action %s"%(coll_id, type_id, action))
        # log.info("  form data %r"%(request.POST))
        http_response = (
            self.get_coll_type_data(coll_id, type_id) or
            self.form_edit_auth(action, recordtypedata._entityuri)
            )
        if http_response:
            return http_response
        # Get key POST values
        entity_id            = request.POST.get('entity_id', None)
        orig_entity_id       = request.POST.get('orig_entity_id', None)
        collection_edit_uri  = self.view_uri(
            'EntityDefaultEditView', 
            coll_id=coll_id, type_id=type_id, entity_id=entity_id
            )
        continuation_uri     = request.POST.get('continuation_uri', collection_edit_uri)









        context_extra_values = (
            { 'coll_id':          coll_id
            , 'continuation_uri': continuation_uri
            })
        messages = (
            { 'parent_heading':    message.COLLECTION_ID
            , 'parent_missing':    message.COLLECTION_NOT_EXISTS%(coll_id)
            , 'entity_heading':    message.RECORD_TYPE_ID
            , 'entity_invalid_id': message.RECORD_TYPE_ID_INVALID
            , 'entity_exists':     message.RECORD_TYPE_EXISTS%(type_id, coll_id)
            , 'entity_not_exists': message.RECORD_TYPE_NOT_EXISTS%(type_id, coll_id)        
            })
        return self.form_response(request, action, coll, type_id, orig_type_id, messages, context_extra_values)





# End.
