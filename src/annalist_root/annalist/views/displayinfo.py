"""
This module defines a class that is used to gather information about an entity
list or view display that is needed to process various kinds of HTTP request.

The intent of this module is to collect and isolate various housekeeping functions
into a common module to avoid repetition of logic and reduce code clutter in
the various Annalist view processing handlers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from collections                    import OrderedDict
from distutils.version              import LooseVersion
import json
import re
import urlparse
import traceback
import logging
log = logging.getLogger(__name__)

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

import annalist
from annalist                       import message
from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.util                  import valid_id, extract_entity_id

from annalist.models.entitytypeinfo import EntityTypeInfo, SITE_PERMISSIONS
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordtypedata import RecordTypeData
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.recordfield    import RecordField
from annalist.models.recordgroup    import RecordGroup
from annalist.models.recordvocab    import RecordVocab

from annalist.views.uri_builder     import (
    uri_param_dict,
    scope_params,
    uri_params, uri_with_params, 
    continuation_url_chain, continuation_chain_url,
    url_update_type_entity_id
    )
from annalist.views.fields.render_entityid  import EntityIdValueMapper


#   -------------------------------------------------------------------------------------------
#
#   Table of authorization symbols added to the display context according to 
#   permissions help by the requesting user
#
#   -------------------------------------------------------------------------------------------

authorization_map = (
    { "auth_create":        ["CREATE"]
    , "auth_delete":        ["DELETE"]
    , "auth_update":        ["UPDATE"]
    , "auth_config":        ["CONFIG"]
    , "auth_create_coll":   ["CREATE_COLLECTION", "ADMIN"]
    , "auth_delete_coll":   ["DELETE_COLLECTION", "ADMIN"]
    })

#   -------------------------------------------------------------------------------------------
#
#   Helper functions
#
#   -------------------------------------------------------------------------------------------

def make_data_ref(request_url, data_ref, resource_type=None):
    """
    Returns a URL reference rel.atiove to the suppliued request_url 
    that can be used as a reference to a data resource based on
    the supplied request URL, data reference and optional type.

    Scope-repated query parameters from the original request_url are 
    preserved, and others are discarded.
    """
    params = scope_params(uri_param_dict(request_url))
    if resource_type:
        params['type'] = resource_type
    return uri_with_params(data_ref, params)

def apply_substitutions(context, text_in):
    """
    Apply substitutions from the supplied `context` to the text supplied as `text_in`,
    returning the resulting string.  This has been introduced to make it easier to 
    create meaningful links in help pages, with values HOST, SITE, COLL and BASE
    added to the context to make references to the current host, site, collection
    and entity base URI respectively.

    Substitutions are made for the following patterns found in `text_in`

    `$name` followed by a non-alphanumeric, non-':' character
    `$name:`
    `$[curie]`
    `$$`

    In the first two, `name` consists of a sequence of alphabetic, numeric or '_' 
    characters, and the pattern is replaced by the corresponding value from the context.

    In the this pattern, `curie` may contain several additional characters that may occur 
    in a compact URI (CURIE); the pattern is replaced by the corresponding context value.

    The final pattern is an escape sequence for inserting a single '$' into the output 
    which might otherwise be treated as a context value substitution.

    If no corresponding context value is found for a substitution pattern, the pattern is
    copied as-is to the output.

    Any other occurrence of '$' (i.e. not part of any pattern above) is untouched.

    >>> context = { 'aa': '-aa-', 'bb': '-bb-', 'c:c': '-cc-'}
    >>> apply_substitutions(context, "foo bar")
    'foo bar'
    >>> apply_substitutions(context, "foo $aa bar")
    'foo -aa- bar'
    >>> apply_substitutions(context, "foo $bb:bar")
    'foo -bb-bar'
    >>> apply_substitutions(context, "foo $[c:c] bar")
    'foo -cc- bar'
    >>> apply_substitutions(context, "foo $$ bar")
    'foo $ bar'
    >>> apply_substitutions(context, "foo $dd bar")
    'foo $dd bar'
    >>> apply_substitutions(context, "foo $ee bar")
    'foo $ee bar'
    >>> apply_substitutions(context, "foo $[f:f] bar")
    'foo $[f:f] bar'
    >>> apply_substitutions(context, "foo $aa $bb: $[c:c] $[f:f] bar")
    'foo -aa- -bb- -cc- $[f:f] bar'
    """
    def sub_fn(matchobj):
        matched = matchobj.group(1) or matchobj.group(2)
        if matchobj.group(3):
            return "$"
        elif matched in context:
            return context[matched]
        return matchobj.group(0)
    namechars  = "_A-Za-z0-9"
    curiechars = "-@.~+*=:;,/?#!"+namechars
    #                          1----)       2----)     3--)
    sub_re     = re.compile("\$([%s]+):?|\$\[([%s]+)\]|\$(\$)"%(namechars, curiechars))
    text_out   = sub_re.sub(sub_fn, text_in)
    return text_out

#   -------------------------------------------------------------------------------------------
#
#   Display information class
#
#   -------------------------------------------------------------------------------------------

class DisplayInfo(object):
    """
    This class collects and organizes common information needed to process various
    kinds of view requests.

    A number of methods are provided that collect different kinds of information,
    allowing the calling method flexibility over what information is actually 
    gathered.  All methods follow a common pattern loosely modeled on an error
    monad, which uses a Django HttpResponse object to record the first problem
    found in the information gathering chain.  Once an error has been detected, 
    subsequent methods do not update the display information, but simply return
    the error response object.

    The information gathering methods do have some dependencies and must be
    invoked in a sequence that ensures the dependencies are satisfied.

    view                is the view object that is being rendered.  This is an instance
                        of a class derived from `AnnalistGenericView`, which in turn is 
                        derived from `django.views.generic.View`.
    action              is the user action for which the form has ben invoked
                        (e.g. "new", "copy", "edit", etc.)
    request_dict        is a dictionary of request parameters
                        For GET requests, this derives from the URI query parameters; 
                        for POST requests it is derived from the submitted form data.
    default_continue    is a default continuation URI to be used when returning from the 
                        current view without an explciitly specified continuation in
                        the request.
    """

    def __init__(self, view, action, request_dict, default_continue):
        self.view               = view
        self.action             = action
        self.is_saved           = False
        self.request_dict       = request_dict
        self.continuation_url   = request_dict.get('continuation_url', None)
        self.default_continue   = default_continue
        # Type/Entity ids from form
        self.orig_type_id       = None
        self.orig_entity_id     = None
        self.curr_type_id       = None
        self.curr_entity_id     = None
        # Type-specific messages
        self.type_messages      = None
        # Default no permissions:
        self.authorizations     = dict([(k, False) for k in authorization_map])
        self.reqhost            = None
        self.site               = None
        self.sitedata           = None
        self.coll_id            = None
        self.collection         = None
        self.coll_perms         = None  # Collection used for permissions checking
        self.type_id            = None
        self.entitytypeinfo     = None
        self.list_id            = None
        self.recordlist         = None
        self.view_id            = None
        self.recordview         = None
        self.entitydata         = None
        self.http_response      = None
        return

    def set_type_entity_id(self,
        orig_type_id=None, orig_entity_id=None,
        curr_type_id=None, curr_entity_id=None
        ):
        """
        Save type and entity ids from form
        """
        self.orig_type_id       = EntityIdValueMapper.decode(orig_type_id)
        self.orig_entity_id     = EntityIdValueMapper.decode(orig_entity_id)
        self.curr_type_id       = EntityIdValueMapper.decode(curr_type_id)
        self.curr_entity_id     = EntityIdValueMapper.decode(curr_entity_id)
        return self.http_response

    def set_messages(self, messages):
        """
        Save type-specific messages for later reporting
        """
        self.type_messages      = messages
        return self.http_response

    def get_site_info(self, reqhost):
        """
        Get site information: site entity object and a copy of the site description data.
        Also saves a copy of the host name to which the current request was directed.
        """
        if not self.http_response:
            self.reqhost        = reqhost
            self.site           = self.view.site(host=reqhost)
            self.sitedata       = self.view.site_data()
        return self.http_response

    def get_coll_info(self, coll_id):
        """
        Check collection identifier, and get reference to collection object.
        """
        assert (self.site is not None)
        if not self.http_response:
            if not Collection.exists(self.site, coll_id):
                self.http_response = self.view.error(
                    dict(self.view.error404values(),
                        message=message.COLLECTION_NOT_EXISTS%{'id': coll_id}
                        )
                    )
            else:
                self.coll_id    = coll_id
                #@@TODO: try with altscope="site"?
                self.collection = Collection.load(self.site, coll_id, altscope="all")
                self.coll_perms = self.collection
                ver = self.collection.get(ANNAL.CURIE.software_version, None) or "0.0.0"
                if LooseVersion(ver) > LooseVersion(annalist.__version__):
                    self.http_response = self.view.error(
                        dict(self.view.error500values(),
                            message=message.COLLECTION_NEWER_VERSION%{'id': coll_id, 'ver': ver}
                            )
                        )
        return self.http_response

    def update_coll_version(self):
        """
        Called when an entity has been updatred to also update the data version 
        associated with the collection if it was previously created by an older 
        version of Annalist.
        """
        assert (self.collection is not None)
        if not self.http_response:
            ver = self.collection.get(ANNAL.CURIE.software_version, None) or "0.0.0"
            if LooseVersion(ver) < LooseVersion(annalist.__version_data__):
                self.collection[ANNAL.CURIE.software_version] = annalist.__version_data__
                self.collection._save()
        return

    def saved(self, is_saved=None):
        """
        Make note that current entity has been saved, and/or return saved status
        """
        if is_saved is not None:
            self.is_saved = is_saved
        return self.is_saved

    def get_type_info(self, type_id):
        """
        Check type identifier, and get reference to type information object.
        """
        if not self.http_response:
            assert ((self.site and self.collection) is not None)
            if type_id:
                self.type_id        = type_id
                self.entitytypeinfo = EntityTypeInfo(self.collection, type_id)
                if not self.entitytypeinfo.recordtype:
                    # log.warning("DisplayInfo.get_type_data: RecordType %s not found"%type_id)
                    self.http_response = self.view.error(
                        dict(self.view.error404values(),
                            message=message.RECORD_TYPE_NOT_EXISTS%(
                                {'id': type_id, 'coll_id': self.coll_id})
                            )
                        )
        return self.http_response

    def get_list_info(self, list_id):
        """
        Retrieve list definition to use for display
        """
        if not self.http_response:
            assert ((self.site and self.collection) is not None)
            assert list_id
            # log.debug(
            #     "DisplayInfo.get_list_info: collection.get_alt_entities %r"%
            #     [ c.get_id() for c in  self.collection.get_alt_entities(altscope="all") ]
            #     )
            if not RecordList.exists(self.collection, list_id, altscope="all"):
                log.warning("DisplayInfo.get_list_info: RecordList %s not found"%list_id)
                self.http_response = self.view.error(
                    dict(self.view.error404values(),
                        message=message.RECORD_LIST_NOT_EXISTS%(
                            {'id': list_id, 'coll_id': self.coll_id})
                        )
                    )
            else:
                self.list_id    = list_id
                self.recordlist = RecordList.load(self.collection, list_id, altscope="all")
                if "@error" in self.recordlist:
                    self.http_response = self.view.error(
                        dict(self.view.error500values(),
                            message=message.RECORD_LIST_LOAD_ERROR%(
                                { 'id':       list_id
                                , 'file':     self.recordlist["@error"]
                                , 'message':  self.recordlist["@message"]
                                })
                            )
                        )
                elif self.type_id is None and self.entitytypeinfo is None:
                    self.get_type_info(
                        extract_entity_id(self.recordlist[ANNAL.CURIE.default_type])
                        )
                # log.debug("DisplayInfo.get_list_info: %r"%(self.recordlist.get_values()))
        return self.http_response

    def get_view_info(self, view_id):
        """
        Retrieve view definition to use for display
        """
        if not self.http_response:
            assert ((self.site and self.collection) is not None)
            if not RecordView.exists(self.collection, view_id, altscope="all"):
                log.warning("DisplayInfo.get_view_info: RecordView %s not found"%view_id)
                log.warning("Collection: %r"%(self.collection))
                log.warning("Collection._altparent: %r"%(self.collection._altparent))
                # log.warning("\n".join(traceback.format_stack()))
                self.http_response = self.view.error(
                    dict(self.view.error404values(),
                        message=message.RECORD_VIEW_NOT_EXISTS%(
                            {'id': view_id, 'coll_id': self.coll_id})
                        )
                    )
            else:
                self.view_id    = view_id
                self.recordview = RecordView.load(self.collection, view_id, altscope="all")
                if "@error" in self.recordview:
                    self.http_response = self.view.error(
                        dict(self.view.error500values(),
                            message=message.RECORD_VIEW_LOAD_ERROR%(
                                { 'id':       list_id
                                , 'file':     self.recordview["@error"]
                                , 'message':  self.recordview["@message"]
                                })
                            )
                        )
                # log.debug("DisplayInfo.get_view_info: %r"%(self.recordview.get_values()))
        return self.http_response

    def get_entity_info(self, action, entity_id):
        """
        Set up entity id and info to use for display

        Also handles some special case permissions settings if the entity is a Collection.
        """
        if not self.http_response:
            assert self.entitytypeinfo is not None
            self.src_entity_id  = entity_id
            if action in ["new", "copy"]:
                self.use_entity_id = self.entitytypeinfo.entityclass.allocate_new_id(
                    self.entitytypeinfo.entityparent, base_id=entity_id
                    )
            else:
                self.use_entity_id  = entity_id
            # Special case permissions when accessing collection metadata:
            # use the collection itself rather than the site data collection to which it belongs.
            if self.type_id == "_coll":
                # log.info("DisplayInfo.get_entity_info: access collection data for %s"%entity_id)
                c = Collection.load(self.site, entity_id, altscope="all")
                if c:
                    self.coll_perms = c
        return self.http_response

    def check_authorization(self, action):
        """
        Check authorization.  Return None if all is OK, or HttpResonse object.

        Also, save copy of key authorizations for later rendering.
        """
        if not self.http_response:
            # Save key authorizations for later rendering
            for k in authorization_map:
                for p in authorization_map[k]:
                    self.authorizations[k] = (
                        self.authorizations[k] or 
                        self.view.authorize(p, self.coll_perms) is None
                        )
            # Check requested action
            action = action or "view"
            if self.entitytypeinfo:
                # print "@@ type permissions map, action %s"%action
                permissions_map = self.entitytypeinfo.permissions_map
            else:
                # Use Collection permissions map
                # print "@@ site permissions map, action %s"%action
                permissions_map = SITE_PERMISSIONS
                # raise ValueError("displayinfo.check_authorization without entitytypeinfo")
                # # permissions_map = {}

            # Previously, default permission map was applied in view.form_action_auth if no 
            # type-based map was provided.
            self.http_response = (
                self.http_response or 
                self.view.form_action_auth(action, self.coll_perms, permissions_map)
                )
        return self.http_response

    def report_error(self, message):
        log.error(message)
        if not self.http_response:
            self.http_response = self.view.error(
                dict(self.view.error400values(),
                    message=message
                    )
                )
        return self.http_response

    # Additional support functions for collection view

    def get_default_view(self):
        """
        Return default view_id, type_id and entity_id to display for collection,
        or None for any values not defined.
        """
        return self.collection.get_default_view()

    # Additonal support functions for list views

    def get_type_list_id(self, type_id):
        """
        Return default list_id for listing defined type, or None
        """
        list_id = None
        # print "@@ get_type_list_id type_id %s, list_id %s"%(type_id, list_id)
        if type_id:
            if self.entitytypeinfo.recordtype:
                list_id = extract_entity_id(
                    self.entitytypeinfo.recordtype.get(ANNAL.CURIE.type_list, None)
                    )
            else:
                log.warning("DisplayInfo.get_type_list_id no type data for %s"%(type_id))
        # print "@@ get_type_list_id %s"%list_id
        return list_id

    def get_list_id(self, type_id, list_id):
        """
        Return supplied list_id if defined, otherwise find default list_id for
        entity type or collection (unless an error has been detected).
        """
        # print "@@ get_list_id 1 %s"%list_id
        if not self.http_response:
            list_id = (
                list_id or 
                self.get_type_list_id(type_id) or
                self.collection.get_default_list() or
                ("Default_list" if type_id else "Default_list_all")
                )
            # print "@@ get_list_id 2 %s"%list_id
            if not list_id:
                log.warning("get_list_id: %s, type_id %s"%(list_id, type_id))
            # print "@@ get_list_id 3 %s"%list_id
        return list_id

    def get_list_view_id(self):
        return extract_entity_id(
            self.recordlist.get(ANNAL.CURIE.default_view, None) or "Default_view"
            )

    def get_list_type_id(self):
        return extract_entity_id(
            self.recordlist.get(ANNAL.CURIE.default_type, None) or "Default_type"
            )

    def check_collection_entity(self, entity_id, entity_type, msg):
        """
        Test a supplied entity_id is defined in the current collection,
        returning a URI to display a supplied error message if the test fails.

        NOTE: this function works with the generic base template base_generic.html, which
        is assumed to provide an underlay for the currently viewed page.

        entity_id           entity id that is required to be defined in the current collection.
        entity_type         specified type for entity to delete.
        msg                 message to display if the test fails.

        returns a URI string for use with HttpResponseRedirect to redisplay the 
        current page with the supplied message, or None if entity id is OK.
        """
        # log.info("check_collection_entity: entity_id: %s"%(entity_id))
        # log.info("check_collection_entity: entityparent: %s"%(self.entityparent.get_id()))
        # log.info("check_collection_entity: entityclass: %s"%(self.entityclass))
        redirect_uri = None
        typeinfo     = self.entitytypeinfo
        if not typeinfo or typeinfo.get_type_id() != entity_type:
            typeinfo = EntityTypeInfo(self.collection, entity_type)
        if not typeinfo.entityclass.exists(typeinfo.entityparent, entity_id):
            redirect_uri = (
                uri_with_params(
                    self.view.get_request_path(),
                    self.view.error_params(msg),
                    self.get_continuation_url_dict()
                    )
                )
        return redirect_uri

    def get_new_view_uri(self, coll_id, type_id):
        """
        Get URI for entity new view from list display
        """
        return self.view.view_uri(
            "AnnalistEntityNewView", 
            coll_id=coll_id, 
            view_id=self.get_list_view_id(), 
            type_id=type_id,
            action="new"
            )

    def get_edit_view_uri(self, coll_id, type_id, entity_id, action):
        """
        Get URI for entity edit or copy view from list display
        """
        return self.view.view_uri(
                "AnnalistEntityEditView", 
                coll_id=coll_id, 
                view_id=self.get_list_view_id(), 
                type_id=type_id,
                entity_id=entity_id,
                action=action
                )

    # Additonal support functions

    def get_view_id(self, type_id, view_id):
        """
        Get view id or suitable default using type if defined.
        """
        if not self.http_response:
            view_id = (
                view_id or 
                self.entitytypeinfo.get_default_view_id()
                )
            if not view_id:
                log.warning("get_view_id: %s, type_id %s"%(view_id, self.type_id))
        return view_id

    def get_continuation_param(self):
        """
        Return continuation URL specified for the current request, or None.
        """
        cont_here = self.view.continuation_here(self.request_dict, self.default_continue)
        return uri_params({"continuation_url": cont_here})

    def get_continuation_url(self):
        """
        Return continuation URL specified for the current request, or None.
        """
        return self.continuation_url

    def get_continuation_url_dict(self):
        """
        Return dictionary with continuation URL specified for the current request.
        """
        c = self.get_continuation_url()
        return {'continuation_url': c} if c else {}

    def get_continuation_next(self):
        """
        Return continuation URL to be used when returning from the current view.

        Uses the default continuation if no value supplied in request dictionary.
        """
        log.debug(
            "get_continuation_next '%s', default '%s'"%
              (self.continuation_url, self.default_continue)
            )
        return self.continuation_url or self.default_continue

    def get_continuation_here(self, base_here=None):
        """
        Return continuation URL back to the current view.
        """
        # @@TODO: consider merging logic from generic.py, and eliminating method there
        return self.view.continuation_here(
            request_dict=self.request_dict,
            default_cont=self.get_continuation_url(),
            base_here=base_here
            )

    def update_continuation_url(self, 
        old_type_id=None, new_type_id=None, 
        old_entity_id=None, new_entity_id=None
        ):
        """
        Update continuation URI to reflect renamed type or entity.
        """
        # def update_hop(chop):
        #     return url_update_type_entity_id(chop, 
        #         old_type_id=old_type_id, new_type_id=new_type_id, 
        #         old_entity_id=old_entity_id, new_entity_id=new_entity_id
        #         )
        curi = self.continuation_url
        if curi:
            hops = continuation_url_chain(curi)
            for i in range(len(hops)):
                uribase, params = hops[i]
                uribase = url_update_type_entity_id(uribase, 
                    old_type_id=old_type_id, new_type_id=new_type_id, 
                    old_entity_id=old_entity_id, new_entity_id=new_entity_id
                    )
                hops[i] = (uribase, params)
            curi = continuation_chain_url(hops)
            self.continuation_url = curi
        return curi

    def get_entity_data_ref(self, return_type=None):
        """
        Returns a string that can be used as a reference to the entity metadata resource
        relative to an entity URL, optionally with a specified type parameter added.
        """
        assert self.entitytypeinfo is not None
        return make_data_ref(
            self.view.get_request_path(), 
            self.entitytypeinfo.entityclass._entityfile, 
            return_type
            )

    def get_entity_list_ref(self, return_type=None):
        """
        Returns a string that can be used as a reference to the entity list data
        relative to the current list URL.
        """
        return make_data_ref(
            self.view.get_request_path(), 
            layout.ENTITY_LIST_FILE, 
            return_type
            )

    def context_data(self, entity_label=None):
        """
        Return dictionary of rendering context data available from the 
        elements assembled.

        Values that are added here to the view context are used for view rendering, 
        and are not passed to the entity value mapping process.

        NOTE: values that are needed to be accessible as part of bound_field values 
        must be provided earlier in the form generation process, as elements of the 
        "context_extra_values" dictionary.

        Context values set here do not need to be named in the valuye maop used to
        create the view context.
        """
        site_url_parts = urlparse.urlsplit(self.site._entityurl)
        context = (
            { 'site_label':         self.sitedata["title"]
            , 'title':              self.sitedata["title"]
            , 'heading':            self.sitedata["title"]
            , 'action':             self.action
            , 'coll_id':            self.coll_id
            , 'type_id':            self.type_id
            , 'view_id':            self.view_id
            , 'list_id':            self.list_id
            , "SITE":               site_url_parts.path
            , "HOST":               self.reqhost
            })
        context.update(self.authorizations)
        if self.collection:
            coll_url_parts = urlparse.urlsplit(self.collection._entityurl)
            context.update(
                { 'heading':    self.collection[RDFS.CURIE.label]
                , 'coll_label': self.collection[RDFS.CURIE.label]
                , "COLL":       coll_url_parts.path
                , "BASE":       coll_url_parts.path + layout.COLL_BASE_REF
                })
            context['title'] = "%(coll_label)s"%context
        if self.recordview:
            context.update(
                { 'heading':            self.recordview[RDFS.CURIE.label]
                , 'view_label':         self.recordview[RDFS.CURIE.label]
                , 'edit_view_button':   self.recordview.get(ANNAL.CURIE.open_view, "yes")
                })
            context['title'] = "%(view_label)s - %(coll_label)s"%context
            edit_task_buttons = self.recordview.get(ANNAL.CURIE.edit_task_buttons, None)
            view_task_buttons = self.recordview.get(ANNAL.CURIE.view_task_buttons, None)
            self.add_task_button_context('edit_task_buttons', edit_task_buttons, context)
            self.add_task_button_context('view_task_buttons', view_task_buttons, context)
        if self.recordlist:
            context.update(
                { 'heading':                self.recordlist[RDFS.CURIE.label]
                , 'list_label':             self.recordlist[RDFS.CURIE.label]
                , 'entity_list_ref':        self.get_entity_list_ref()
                , 'entity_list_ref_json':   self.get_entity_list_ref("application/json")
                })
            context['title'] = "%(list_label)s - %(coll_label)s"%context
        if self.entitytypeinfo:
            context.update(
                { 'entity_data_ref':        self.get_entity_data_ref()
                , 'entity_data_ref_json':   self.get_entity_data_ref("application/json")
                })
        if entity_label:
            context.update(
                { 'entity_label':       entity_label
                })
            # context['heading'] = "%(entity_label)s - %(view_label)s"%context
            context['title']   = "%(entity_label)s - %(view_label)s - %(coll_label)s"%context
        if hasattr(self.view, 'help') and self.view.help:
            context.update(
                { 'help_filename':  self.view.help
                })
        if hasattr(self.view, 'help_markdown') and self.view.help_markdown:
            substituted_text = apply_substitutions(context, self.view.help_markdown)
            context.update(
                { 'help_markdown':  substituted_text
                })
        return context

    def add_task_button_context(self, task_buttons_name, task_buttons, context):
        """
        Adds context values to a supplied context dictionary corresponding 
        to the supplied task_buttons value(s) from a view description.

        @NOTE: subsequent versions of this function may extract values from
        an identified task description record.
        """
        if isinstance(task_buttons, list):
            context.update(
                { task_buttons_name:
                    [ { 'button_id':    b[ANNAL.CURIE.button_id]
                      , 'button_name':  extract_entity_id(b[ANNAL.CURIE.button_id])
                      , 'button_label': b.get(ANNAL.CURIE.button_label, "@@annal:button_label@@")
                      , 'button_help':  b.get(ANNAL.CURIE.button_help,  "@@annal:button_help@@")
                      } for b in task_buttons
                    ]
                })
        elif task_buttons is not None:
            log.error(
                "DisplayInfo.context_data: Unexpected value for task_buttons: %r"%
                (task_buttons)
                )
        return

    def __str__(self):
        attrs = (
            [ "view"
            , "action"
            , "authorizations"
            , "reqhost"
            , "site"
            , "sitedata"
            , "coll_id"
            , "collection"
            , "type_id"
            , "entitytypeinfo"
            , "list_id"
            , "recordlist"
            , "view_id"
            , "recordview"
            , "entity_id"
            ])
        fields = ["DisplayInfo("]
        for attr in attrs:
            val = getattr(self, attr, None)
            if val is not None:
                fields.append("%s: %r"%(attr, val))
        fields.append(")")
        return ("\n  ".join(fields))

    def __repr__(self):
        return str(self)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
