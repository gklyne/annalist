"""
Entity list view
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from django.conf                        import settings
from django.http                        import HttpResponse
from django.http                        import HttpResponseRedirect
from django.core.urlresolvers           import resolve, reverse

from annalist                           import message
from annalist.exceptions                import Annalist_Error
from annalist.identifiers               import RDFS, ANNAL
from annalist.util                      import split_type_entity_id, extract_entity_id

from annalist.models.collection         import Collection
from annalist.models.recordtype         import RecordType
from annalist.models.recordtypedata     import RecordTypeData
from annalist.models.entitytypeinfo     import EntityTypeInfo, CONFIG_PERMISSIONS
from annalist.models.entityfinder       import EntityFinder

from annalist.views.uri_builder         import uri_with_params
from annalist.views.displayinfo         import DisplayInfo
from annalist.views.confirm             import ConfirmView, dict_querydict
from annalist.views.generic             import AnnalistGenericView

from annalist.views.fielddescription    import FieldDescription, field_description_from_view_field
from annalist.views.entityvaluemap      import EntityValueMap
from annalist.views.simplevaluemap      import SimpleValueMap, StableValueMap
from annalist.views.fieldlistvaluemap   import FieldListValueMap
from annalist.views.fieldvaluemap       import FieldValueMap
from annalist.views.repeatvaluesmap     import RepeatValuesMap

from annalist.views.fields.bound_field  import bound_field, get_entity_values

#   -------------------------------------------------------------------------------------------
#
#   Mapping table data (not view-specific)
#
#   -------------------------------------------------------------------------------------------

# Table used as basis, or initial values, for a dynamically generated 
# entity-value map for list displays
listentityvaluemap  = (
        [ SimpleValueMap(c='title',                 e=None,                  f=None                  )
        , SimpleValueMap(c='help_filename',         e=None,                  f=None                  )
        , SimpleValueMap(c='coll_id',               e=None,                  f=None                  )
        , SimpleValueMap(c='coll_label',            e=None,                  f=None                  )
        , SimpleValueMap(c='type_id',               e=None,                  f=None                  )
        , SimpleValueMap(c='list_id',               e=None,                  f=None                  )
        , SimpleValueMap(c='list_label',            e=None,                  f=None                  )
        , SimpleValueMap(c='list_choices',          e=None,                  f=None                  )
        , SimpleValueMap(c='collection_view',       e=None,                  f=None                  )
        , SimpleValueMap(c='default_view_id',       e=None,                  f=None                  )
        , SimpleValueMap(c='default_view_enable',   e=None,                  f=None                  )
        , SimpleValueMap(c='search_for',            e=None,                  f='search_for'          )
        , SimpleValueMap(c='continuation_url',      e=None,                  f='continuation_url'    )
        # Field data is handled separately during processing of the form description
        # Form and interaction control (hidden fields)
        ])

#   -------------------------------------------------------------------------------------------
#
#   List entities view - form rendering and POST response handling
#
#   -------------------------------------------------------------------------------------------

class EntityGenericListView(AnnalistGenericView):
    """
    View class for generic entity list view
    """

    _entityformtemplate = 'annalist_entity_list.html'

    def __init__(self):
        super(EntityGenericListView, self).__init__()
        self.help          = "entity-list-help"
        return

    # Helper functions

    def list_setup(self, coll_id, type_id, list_id, request_dict):
        """
        Assemble display information for list view request handlers
        """
        #@@ self.site_view_url       = self.view_uri("AnnalistSiteView")
        self.collection_view_url = self.view_uri("AnnalistCollectionView", coll_id=coll_id)
        listinfo = DisplayInfo(self, "list", request_dict, self.collection_view_url)
        listinfo.get_site_info(self.get_request_host())
        listinfo.get_coll_info(coll_id)
        listinfo.get_type_info(type_id)
        listinfo.get_list_info(listinfo.get_list_id(listinfo.type_id, list_id))
        listinfo.check_authorization("list")
        return listinfo

    def get_list_entityvaluemap(self, listinfo, context_extra_values):
        """
        Creates an entity/value map table in the current object incorporating
        information from the form field definitions for an indicated list display.
        """
        # Locate and read view description
        entitymap  = EntityValueMap(listentityvaluemap)
        log.debug("entitylist %r"%listinfo.recordlist.get_values())

        # Need to generate
        # 1. 'fields':  (context receives list of field descriptions used to generate row headers)
        # 2. 'entities': (context receives a bound field that displays entry for each entity)

        # NOTE - supplied entity has single field 'annal:list_entities' (see 'get')
        #        entitylist template uses 'fields' from context to display headings

        fieldlistmap = FieldListValueMap('fields',
            listinfo.collection, 
            listinfo.recordlist[ANNAL.CURIE.list_fields],
            None
            )
        entitymap.add_map_entry(fieldlistmap)  # For access to field headings

        repeatrows_field_descr = (
            { ANNAL.CURIE.id:                   "List_rows"
            , RDFS.CURIE.label:                 "Fields"
            , RDFS.CURIE.comment:               "This resource describes the repeated field description used when displaying and/or editing a record view description"
            , ANNAL.CURIE.field_name:           "List_rows"
            , ANNAL.CURIE.field_render_type:    "RepeatListRow"
            , ANNAL.CURIE.property_uri:         "_list_entities_"
            , ANNAL.CURIE.group_ref:            "_group/List_fields"
            })
        repeatrows_group_descr = (
            { ANNAL.CURIE.id:           "List_fields"
            , RDFS.CURIE.label:         "List fields description"
            , ANNAL.CURIE.group_fields: listinfo.recordlist[ANNAL.CURIE.list_fields]
            })
        repeatrows_descr = FieldDescription(
            listinfo.collection, 
            repeatrows_field_descr,
            group_view=repeatrows_group_descr
            )
        entitymap.add_map_entry(FieldValueMap(c="List_rows", f=repeatrows_descr))

        return entitymap

    # GET

    def get(self, request, coll_id=None, type_id=None, list_id=None, scope=None):
        """
        Create a form for listing entities.
        """
        log.info(
            "views.entitylist.get:  coll_id %s, type_id %s, list_id %s, scope %s"%
            (coll_id, type_id, list_id, scope)
            )
        listinfo    = self.list_setup(coll_id, type_id, list_id, request.GET.dict())
        if listinfo.http_response:
            return listinfo.http_response
        log.debug("listinfo.list_id %s"%listinfo.list_id)
        # Prepare list and entity IDs for rendering form
        selector    = listinfo.recordlist.get_values().get(ANNAL.CURIE.list_entity_selector, "")
        search_for  = request.GET.get('search', "")
        user_perms  = self.get_permissions(listinfo.collection)
        entity_list = (
            EntityFinder(listinfo.collection, selector=selector)
                .get_entities_sorted(
                    user_perms, type_id=type_id, scope=scope,
                    context=listinfo.recordlist, search=search_for
                    )
            )
        typeinfo      = listinfo.entitytypeinfo
        entityvallist = { '_list_entities_': [ get_entity_values(typeinfo, e) for e in entity_list ] }
        # Set up initial view context
        context_extra_values = (
            { 'continuation_url':       listinfo.get_continuation_url() or ""
            , 'request_url':            self.get_request_path()
            , 'coll_id':                coll_id
            , 'type_id':                type_id
            , 'list_id':                listinfo.list_id
            , 'search_for':             search_for
            , 'list_choices':           self.get_list_choices_field(listinfo)
            , 'collection_view':        self.collection_view_url
            , 'default_view_id':        listinfo.recordlist[ANNAL.CURIE.default_view]
            , 'default_view_enable':    ("" if list_id else 'disabled="disabled"')
            })
        entityvaluemap = self.get_list_entityvaluemap(listinfo, context_extra_values)
        listcontext = entityvaluemap.map_value_to_context(
            entityvallist,
            **context_extra_values
            )
        listcontext.update(listinfo.context_data())
        # log.debug("EntityGenericListView.get listcontext %r"%(listcontext))
        # Generate and return form data
        return (
            self.render_html(listcontext, self._entityformtemplate) or 
            self.error(self.error406values())
            )

    # POST

    def post(self, request, coll_id=None, type_id=None, list_id=None, scope=None):
        """
        Handle response from dynamically generated list display form.
        """
        log.info("views.entitylist.post: coll_id %s, type_id %s, list_id %s"%(coll_id, type_id, list_id))
        # log.info("  %s"%(self.get_request_path()))
        # log.info("  form data %r"%(request.POST))
        listinfo = self.list_setup(coll_id, type_id, list_id, request.POST.dict())
        if listinfo.http_response:
            return listinfo.http_response
        if 'close' in request.POST:
            return HttpResponseRedirect(listinfo.get_continuation_url() or self.collection_view_url)

        # Process requested action
        redirect_uri = None
        entity_ids   = request.POST.getlist('entity_select')
        log.debug("entity_ids %r"%(entity_ids))
        if len(entity_ids) > 1:
            action = ""
            redirect_uri = self.check_value_supplied(
                None, message.TOO_MANY_ENTITIES_SEL,
                continuation_url=listinfo.get_continuation_url()
                )
        else:
            entity_type = type_id or listinfo.get_list_type_id()
            entity_id   = None
            if len(entity_ids) == 1:
                (entity_type, entity_id) = split_type_entity_id(entity_ids[0], entity_type)
            if "new" in request.POST:
                action = "new"
                redirect_uri = uri_with_params(
                    listinfo.get_new_view_uri(coll_id, entity_type), 
                    {'continuation_url': listinfo.get_continuation_here()}
                    )
            if "copy" in request.POST:
                action = "copy"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_COPY, 
                        continuation_url=listinfo.get_continuation_url()
                        )
                    or
                    uri_with_params(
                        listinfo.get_edit_view_uri(
                            coll_id, entity_type, entity_id, action
                            ),
                        {'continuation_url': listinfo.get_continuation_here()}
                        )
                    )
            if "edit" in request.POST:
                action = "edit"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_EDIT,
                        continuation_url=listinfo.get_continuation_url()
                        )
                    or
                    uri_with_params(
                        listinfo.get_edit_view_uri(
                            coll_id, entity_type, entity_id, action
                            ),
                        {'continuation_url': listinfo.get_continuation_here()}
                        )
                    )
            if "delete" in request.POST:
                action = "delete"
                redirect_uri = (
                    self.check_value_supplied(entity_id, 
                        message.NO_ENTITY_FOR_DELETE,
                        continuation_url=listinfo.get_continuation_url()
                        )
                    or
                    listinfo.check_collection_entity(entity_id, entity_type,
                        message.SITE_ENTITY_FOR_DELETE%{'id': entity_id}
                        )
                    or
                    self.check_delete_type_values(listinfo,
                        entity_id, entity_type,
                        message.TYPE_VALUES_FOR_DELETE%{'type_id': entity_id}
                        )
                    )
                if not redirect_uri:
                    # Get user to confirm action before actually doing it
                    confirmed_action_uri = self.view_uri(
                        "AnnalistEntityDataDeleteView", 
                        coll_id=coll_id, type_id=entity_type
                        )
                    # log.info("coll_id %s, type_id %s, confirmed_action_uri %s"%(coll_id, entity_type, confirmed_action_uri))
                    delete_params = dict_querydict(
                        { "entity_delete":      ["Delete"]
                        , "entity_id":          [entity_id]
                        , "completion_url":     [listinfo.get_continuation_here()]
                        , "search_for":         [request.POST['search_for']]
                        })
                    curi = listinfo.get_continuation_url()
                    if curi:
                        dict_querydict["continuation_url"] = [curi]
                    message_vals = {'id': entity_id, 'type_id': entity_type, 'coll_id': coll_id}
                    typeinfo = listinfo.entitytypeinfo
                    if typeinfo is None:
                        typeinfo = EntityTypeInfo(listinfo.site, listinfo.collection, entity_type)
                    return (
                        self.form_action_auth(
                            "delete", listinfo.collection, typeinfo.permissions_map
                            ) or
                        ConfirmView.render_form(request,
                            action_description=     message.REMOVE_ENTITY_DATA%message_vals,
                            confirmed_action_uri=   confirmed_action_uri,
                            action_params=          delete_params,
                            cancel_action_uri=      listinfo.get_continuation_here(),
                            title=                  self.site_data()["title"]
                            )
                        )
            if "default_view" in request.POST:
                if listinfo.entitytypeinfo:
                    permissions_map = listinfo.entitytypeinfo.permissions_map
                else:
                    permissions_map = CONFIG_PERMISSIONS
                auth_check = self.form_action_auth("config", listinfo.collection, permissions_map)
                if auth_check:
                    return auth_check
                listinfo.collection.set_default_list(list_id)
                action = "list"
                msg    = message.DEFAULT_VIEW_UPDATED%{'coll_id': coll_id, 'list_id': list_id}         
                redirect_uri = (
                    uri_with_params(
                        self.get_request_path(), 
                        self.info_params(msg),
                        listinfo.get_continuation_url_dict()
                        )
                    )
            if ("view" in request.POST) or ("view_all" in request.POST):
                action = "list"         
                search = request.POST['search_for']
                params = listinfo.get_continuation_url_dict()
                if search:
                    params = dict(params, search=search)
                post_list_id = extract_entity_id(request.POST['list_choice'])
                list_uri_params = (
                    { 'coll_id': coll_id
                    , 'list_id': post_list_id
                    })
                if "view_all" in request.POST:
                    list_uri_params['scope']  = "all"
                redirect_uri = (
                    uri_with_params(
                        self.view_uri("AnnalistEntityGenericList", **list_uri_params),
                        params
                        )
                    )
            if "customize" in request.POST:
                action       = "config"
                redirect_uri = (
                    uri_with_params(
                        self.view_uri(
                            "AnnalistCollectionEditView", 
                            coll_id=coll_id
                            ),
                        {'continuation_url': listinfo.get_continuation_here()}
                        )
                    )
        if redirect_uri:
            return (
                listinfo.check_authorization(action) or
                HttpResponseRedirect(redirect_uri)
                )
        # Report unexpected form data
        # This shouldn't happen, but just in case...
        # Redirect to continuation with error
        log.error("Unexpected form data posted to %s: %r"%(request.get_full_path(), request.POST))
        err_values = self.error_params(
            message.UNEXPECTED_FORM_DATA%(request.POST), 
            message.SYSTEM_ERROR
            )
        redirect_uri = uri_with_params(listinfo.get_continuation_next(), err_values)
        return HttpResponseRedirect(redirect_uri)

    def get_list_choices_field(self, listinfo):
        """
        Returns a bound_field object that displays as a list-choice selection drop-down.
        """
        # @@TODO: Possibly create FieldValueMap and return map_entity_to_context value? 
        #         or extract this logic and share?  See also entityedit view choices
        field_description = field_description_from_view_field(
            listinfo.collection, 
            { ANNAL.CURIE.field_id: "List_choice"
            , ANNAL.CURIE.field_placement: "small:0,12;medium:5,5" },
            {}
            )
        entityvals = { field_description['field_property_uri']: listinfo.list_id }
        return bound_field(field_description, entityvals)

    def check_delete_type_values(self, listinfo, entity_id, entity_type, msg):
        """
        Checks for attempt to delete type with existing values

        Returns redirect URI to display error, or None if no error
        """
        if entity_type == "_type":
            typeinfo = EntityTypeInfo(
                listinfo.site, listinfo.collection, entity_id
                )
            if next(typeinfo.enum_entity_ids(), None) is not None:
                return (
                    # Type has values: redisplay form with error message
                    uri_with_params(
                        listinfo.view.get_request_path(),
                        listinfo.view.error_params(msg),
                        listinfo.get_continuation_url_dict()
                        )
                    )
        return None

# End.
