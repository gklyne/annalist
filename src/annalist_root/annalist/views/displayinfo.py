"""
This module defines a class that is used to gather information about an entity
list or view display that is needed to process various kinds of HTTP request.

The intent of this module is to collect and isolate various housekeeping functions
into a common module to avoid repetition of logic and reduce code clutter in
the various Annalist view processing handlers.
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import json
import re
import traceback

from distutils.version              import LooseVersion

from django.conf                    import settings
from django.http                    import HttpResponse
from django.http                    import HttpResponseRedirect
from django.core.urlresolvers       import resolve, reverse

from utils.py3porting               import urljoin, urlsplit

import annalist
from annalist                       import message
from annalist                       import layout
from annalist.identifiers           import RDF, RDFS, ANNAL
from annalist.util                  import valid_id, extract_entity_id

from annalist.models.entitytypeinfo import (
    EntityTypeInfo, 
    SITE_PERMISSIONS, CONFIG_PERMISSIONS
    )
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordlist     import RecordList
from annalist.models.recordview     import RecordView
from annalist.models.annalistuser   import default_user_id, unknown_user_id

from annalist.views.confirm         import ConfirmView, dict_querydict
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

context_authorization_map = (
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
    Returns a URI reference that can be used as a reference a 
    data resource based on the supplied request URL, 
    data resource reference and optional type.

    Scope-related query parameters from the original request_url are 
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
    >>> apply_substitutions(context, "foo bar") == 'foo bar'
    True
    >>> apply_substitutions(context, "foo $aa bar") == 'foo -aa- bar'
    True
    >>> apply_substitutions(context, "foo $bb:bar") == 'foo -bb-bar'
    True
    >>> apply_substitutions(context, "foo $[c:c] bar") == 'foo -cc- bar'
    True
    >>> apply_substitutions(context, "foo $$ bar") == 'foo $ bar'
    True
    >>> apply_substitutions(context, "foo $dd bar") == 'foo $dd bar'
    True
    >>> apply_substitutions(context, "foo $ee bar") == 'foo $ee bar'
    True
    >>> apply_substitutions(context, "foo $[f:f] bar") == 'foo $[f:f] bar'
    True
    >>> apply_substitutions(context, "foo $aa $bb: $[c:c] $[f:f] bar") == 'foo -aa- -bb- -cc- $[f:f] bar'
    True
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
        # Collection/Type/Entity ids - to be supplied based on form data in POST
        self.orig_coll_id       = None
        self.orig_type_id       = None
        self.orig_entity_id     = None
        self.orig_typeinfo      = None
        self.curr_coll_id       = None
        self.curr_type_id       = None
        self.curr_entity_id     = None
        self.curr_typeinfo      = None
        self.src_entity_id      = None
        # Type-specific messages
        self.type_messages      = None
        # Default no permissions:
        self.authorizations     = dict([(k, False) for k in context_authorization_map])
        self.reqhost            = None
        self.site               = None
        self.sitedata           = None
        self.coll_id            = None
        self.collection         = None
        self.orig_coll          = None  # Original collection for copy
        self.perm_coll          = None  # Collection used for permissions checking
        self.type_id            = None  # Type Id from request URI, not dependent on form data
        self.list_id            = None
        self.recordlist         = None
        self.view_id            = None
        self.recordview         = None
        self.entitydata         = None
        # Response data
        self.http_response      = None
        self.info_messages      = []
        self.error_messages     = []
        return

    def set_orig_coll_id(self, orig_coll_id=None):
        """
        For GET and POST operations, set up details of the collection from which
        an existing identified entity is accessible.  This is used later to check 
        collection access permissions.
        """
        self.orig_coll_id       = EntityIdValueMapper.decode(orig_coll_id)
        # If inherited from another collection, update origin collection object
        if self.orig_coll_id and (self.orig_coll_id != self.coll_id):
            c = Collection.load(self.site, self.orig_coll_id, altscope="all")
            if c:
                self.orig_coll = c
        return self.http_response

    def set_coll_type_entity_id(self,
        orig_coll_id=None,
        orig_type_id=None, orig_entity_id=None,
        curr_type_id=None, curr_entity_id=None
        ):
        """
        For a form POST operation, sets updated collection, type and entity
        identifiers from the form data.

        The original collection id may be different by virtue of inheritance
        from another collection (via 'orig_coll_id' parameter).

        The current type identifier may be different by virtue of the type being
        renamed in the form data (via 'curr_type_id' parameter).
        """
        # log.debug(
        #     "@@ DisplaytInfo.set_coll_type_entity_id: %s/%s/%s -> %s/%s"%
        #       ( orig_coll_id, orig_type_id, orig_entity_id, 
        #         curr_type_id, curr_entity_id
        #       )
        #     )
        self.set_orig_coll_id(orig_coll_id)
        if self.http_response:
            return self.http_response
        self.orig_type_id       = EntityIdValueMapper.decode(orig_type_id)
        self.orig_entity_id     = EntityIdValueMapper.decode(orig_entity_id)
        self.curr_type_id       = EntityIdValueMapper.decode(curr_type_id)
        self.curr_entity_id     = EntityIdValueMapper.decode(curr_entity_id)
        if self.orig_coll_id and (self.orig_coll_id != self.coll_id):
            self.orig_typeinfo = EntityTypeInfo(self.orig_coll, orig_type_id)
        if self.curr_type_id and (self.curr_type_id != self.type_id):
            self.curr_typeinfo = EntityTypeInfo(self.collection, curr_type_id)
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
                self.orig_coll  = self.collection
                self.perm_coll  = self.collection
                ver = self.collection.get(ANNAL.CURIE.software_version, None) or "0.0.0"
                if LooseVersion(ver) > LooseVersion(annalist.__version__):
                    self.http_response = self.view.error(
                        dict(self.view.error500values(),
                            message=message.COLLECTION_NEWER_VERSION%{'id': coll_id, 'ver': ver}
                            )
                        )
                self.add_error_messages(self.collection.get_errors())
        return self.http_response

    def flush_collection_caches(self):
        """
        Called to flush collection caches so that changes made independently of 
        the caches can be used.

        NOTE: this is currently called by the top-level collection customize view.
        This is a bit of  a hack to ensure that it is always possible for the user 
        to force caches to be flushed, e.g. when type informatiuon is updated in a 
        different tab or by another user.
        """
        assert (self.collection is not None)
        self.collection.flush_collection_caches()
        return

    def update_coll_version(self):
        """
        Called when an entity has been updated to also update the data version 
        associated with the collection if it was previously created by an older 
        version of Annalist.
        """
        assert (self.collection is not None)
        if not self.http_response:
            self.collection.update_software_compatibility_version()
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
        Check type identifier, and get a reference to the corresponding type 
        information object.

        This method may be called to override the type id from the original request
        URI, and the DisplayInfo 'type_id' value is not updated so that the value
        from the original request URI is not lost.

        See also method 'get_request_type_info'.
        """
        # print "@@@@ get_type_info: type_id %s"%(type_id,)
        if not self.http_response:
            assert ((self.site and self.collection) is not None)
            if type_id:
                self.curr_typeinfo = EntityTypeInfo(self.collection, type_id)
                self.orig_typeinfo = self.curr_typeinfo
                if not self.curr_typeinfo.recordtype:
                    # log.warning("DisplayInfo.get_type_data: RecordType %s not found"%type_id)
                    self.http_response = self.view.error(
                        dict(self.view.error404values(),
                            message=message.RECORD_TYPE_NOT_EXISTS%(
                                {'id': type_id, 'coll_id': self.coll_id})
                            )
                        )
        return self.http_response

    def get_request_type_info(self, type_id):
        """
        Save and check type identifier from request URI, and get a reference to 
        the corresponding type information object.
        """
        self.type_id = type_id
        return self.get_type_info(type_id)

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
            if not self.check_list_id(list_id):
                log.warning("DisplayInfo.get_list_info: RecordList %s not found"%list_id)
                msg1 = message.RECORD_LIST_NOT_EXISTS%{'id': list_id, 'coll_id': self.coll_id}
                self.add_error_message(msg1)
                list_id = self.get_list_id(self.type_id, None)
                msg2 = message.DISPLAY_ALTERNATIVE_LIST%{'id': list_id, 'coll_id': self.coll_id}
                self.add_error_message(msg2)
                #@@
                # self.http_response = self.view.error(
                #     dict(self.view.error404values(),
                #         message=message.RECORD_LIST_NOT_EXISTS%(
                #             {'id': list_id, 'coll_id': self.coll_id})
                #         )
                #     )
                #@@
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
            elif self.type_id is None and self.curr_typeinfo is None:
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
            if not self.check_view_id(view_id):
                log.warning("DisplayInfo.get_view_info: RecordView %s not found"%view_id)
                log.warning("Collection: %r"%(self.collection))
                log.warning("Collection._altparent: %r"%(self.collection._altparent))
                # log.warning("\n".join(traceback.format_stack()))
                msg1 = message.RECORD_VIEW_NOT_EXISTS%{'id': view_id, 'coll_id': self.coll_id}
                self.add_error_message(msg1)
                view_id = self.get_view_id(self.type_id, None)
                msg2 = message.DISPLAY_ALTERNATIVE_VIEW%{'id': view_id, 'coll_id': self.coll_id}
                self.add_error_message(msg2)
                #@@
                # self.http_response = self.view.error(
                #     dict(self.view.error404values(),
                #         message=message.RECORD_VIEW_NOT_EXISTS%(
                #             {'id': view_id, 'coll_id': self.coll_id})
                #         )
                #     )
                #@@
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
            assert self.curr_typeinfo is not None
            self.src_entity_id  = entity_id
            self.curr_entity_id = entity_id
            if action in ["new", "copy"]:
                self.use_entity_id = self.curr_typeinfo.entityclass.allocate_new_id(
                    self.curr_typeinfo.entityparent, base_id=entity_id
                    )
            else:
                self.use_entity_id  = entity_id
            # Special case permissions when accessing collection metadata:
            # use the collection itself rather than the site data collection to which it belongs.
            if self.type_id == "_coll":
                # log.info("DisplayInfo.get_entity_info: access collection data for %s"%entity_id)
                c = Collection.load(self.site, entity_id, altscope="all")
                if c:
                    self.perm_coll = c
        return self.http_response

    # Support methods for response generation

    def check_authorization(self, action):
        """
        Check authorization.  Return None if all is OK, or HttpResonse object.

        Also, save copy of key authorizations for later rendering.
        """
        if not self.http_response:
            # Save key authorizations for later rendering
            for k in context_authorization_map:
                for p in context_authorization_map[k]:
                    self.authorizations[k] = (
                        self.authorizations[k] or 
                        self.view.authorize(p, self.perm_coll) is None
                        )
            # Check requested action
            action = action or "view"
            if self.curr_typeinfo:
                # log.info(
                #     "@@ check_authorization (curr) action %s, type_id %s, entity_id %s"%
                #     (action, self.curr_typeinfo.type_id, self.curr_entity_id)
                #     )
                permissions_map = (
                    self.curr_typeinfo.get_entity_permissions_map(self.curr_entity_id)
                    )
            else:
                # Use site permissions map (some site operations don't have an entity type?)
                permissions_map = SITE_PERMISSIONS
            # Previously, default permission map was applied in view.form_action_auth if no 
            # type-based map was provided.
            self.http_response = (
                self.http_response or 
                self.view.form_action_auth(
                    action, self.perm_coll, permissions_map,
                    continuation_url=self.get_continuation_here()
                    )
                )
        if ( (not self.http_response) and 
             (self.orig_coll_id) and 
             (self.orig_coll_id != self.perm_coll.get_id()) ):
            # Copying content from different collection: check access
            if self.orig_typeinfo:
                # log.info(
                #     "@@ check_authorization (orig) action %s, type_id %s, entity_id %s"%
                #     (action, self.orig_typeinfo.type_id, self.orig_entity_id)
                #     )
                orig_permissions_map = (
                    self.orig_typeinfo.get_entity_permissions_map(self.orig_entity_id)
                    )
            else:
                orig_permissions_map = SITE_PERMISSIONS
            self.http_response = self.view.form_action_auth("view", 
                self.orig_coll, orig_permissions_map,
                continuation_url=self.get_continuation_here()
                )
        return self.http_response

    #@@TODO: not sure if this will be useful...
    # def reset_info_messages(self):
    #     """
    #     Reset informational messages (for form redisplay)
    #     cf. entityedit.form_re_render
    #     """
    #     self.info_messages      = []
    #     return
    #@@

    def add_info_message(self, message):
        """
        Save message to be displayed on successful completion
        """
        self.info_messages.append(message)
        return self.http_response

    def add_error_message(self, message):
        """
        Save error message to be displayed on completion of the current operation
        """
        self.error_messages.append(message)
        return self.http_response

    def add_error_messages(self, messages):
        """
        Save list of error message to be displayed on completion of the current operation
        """
        # print "@@ add_error_messages: > %r"%(messages,)
        self.error_messages.extend(messages)
        # print "@@ add_error_messages: < %r"%(self.error_messages,)
        return self.http_response

    def redisplay_path_params(self):
        """
        Gathers URL details based on the current request URL that can be used 
        to construct a URL to redisplay the current page.

        Returns a pair of values:

            redisplay_path, redisplay_params

        Where 'redisplay_path' is the URL path for the current request,
        and 'redisplay_params' is a selection of request URL parameters that 
        are used to select data for the current display (see 'scope_params').
        """
        redisplay_path   = self.view.get_request_path()
        redisplay_params = scope_params(uri_param_dict(redisplay_path))
        redisplay_params.update(self.get_continuation_url_dict())
        return (redisplay_path, redisplay_params)

    def redirect_response(self, redirect_path, redirect_params={}, action=None):
        """
        Return an HTTP redirect response, with information or warning messages as
        requested included as parameters.

        redirect_path   the URI base path to redirect to.
        redirect_params an optional dictionary of parameters to be applied to the 
                        redirection URI.
        action          an action that must be authorized if the redirection is to occur,
                        otherwise an error is reported and the current page redisplayed.
                        If None or not supplied, no authorization check is performed.

        Returns an HTTP response value.
        """
        # @TODO: refactor existing redirect response code (here and in list/edit modules)
        #        to use this method.  (Look for other instances of HttpResponseRedirect)
        # print "@@ redirect_response: http_response %r"%(self.http_response,)
        if not self.http_response:
            redirect_msg_params = dict(redirect_params)
            if self.info_messages:
                redirect_msg_params.update(self.view.info_params("\n\n".join(self.info_messages)))
            if self.error_messages:
                redirect_msg_params.update(self.view.error_params("\n\n".join(self.error_messages)))
            # print "@@ redirect_response: redirect_msg_params %r"%(redirect_msg_params,)
            redirect_uri = (
                uri_with_params(
                    redirect_path,
                    redirect_msg_params
                    )
                )
            self.http_response = (
                (action and self.check_authorization(action))
                or
                HttpResponseRedirect(redirect_uri)
                )
        return self.http_response

    def display_error_response(self, err_msg):
        """
        Return an HTTP response that redisplays the current view with an error
        message displayed.

        err_msg         is the error message to be displayed.
        """
        redirect_path, redirect_params = self.redisplay_path_params()
        self.add_error_message(err_msg)
        return self.redirect_response(redirect_path, redirect_params=redirect_params)

    def report_error(self, message):
        """
        Set up error response
        """
        log.error(message)
        if not self.http_response:
            self.http_response = self.view.error(
                dict(self.view.error400values(),
                    message=message
                    )
                )
        return self.http_response

    def confirm_delete_entity_response(self, 
            entity_type_id, entity_id, 
            complete_action_uri,
            form_action_field="entity_delete",
            form_value_field="entity_id",
            response_messages = {}
            ):
        """
        This method generates a response when the user has requested deletion
        of an entity from the current collection.  It includes logic to request 
        confirmation of the requested action before proceeding to actually remove
        the entity.

        The request for confirmation is handled via class "ConfirmView" (confirm.py),
        and actual deletion and continuation is performed via the view specified by
        "complete_action_view", which is typically realized by a subclass of 
        "EntityDeleteConfirmedBaseView" (entitydeletebase.py)

        entity_type_id          is the type id of the entity to be deleted.
        entity_id               is the entity id of the entity to be deleted.
        complete_action_uri     identifies a view to be invoked by an HTTP POST operation
                                to complete the entity deletion.
        form_action_field       names the form field that is used to trigger entity deletion
                                in the completion view.  Defaults to "entity_delete"
        form_value_field        names the form field that is used to provide the identifier of
                                the entity or entities to be deleted.
        response_messages       is a dictionary of messages to be used to indicate 
                                various outcomes:
                                "no_entity" is the entity for deletion is not specified.
                                "cannot_delete" if entity does not exist or cannot be deleted.
                                "confirm_completion" to report co,mpletion of entity deletion.
                                If no message dictionary is provided, or if no value is provided 
                                for a particular outcome, a default message value will be used.
                                Messages may use value interpolation for %(type_id)s and %(id)s.
        """
        def _get_message(msgid):
            return response_messages.get(msgid, default_messages.get(msgid)%message_params)

        default_messages = (
            { "no_entity":          message.NO_ENTITY_FOR_DELETE
            , "cannot_delete":      message.CANNOT_DELETE_ENTITY
            , "type_has_values":    message.TYPE_VALUES_FOR_DELETE
            , "confirm_completion": message.REMOVE_ENTITY_DATA
            })
        entity_coll_id = self.collection.get_id()
        message_params = (
            { "id":         entity_id
            , "type_id":    entity_type_id
            , "coll_id":    entity_coll_id
            })

        if not entity_id:
            self.display_error_response(_get_message("no_entity"))
        elif not self.entity_exists(entity_id, entity_type_id):
            self.display_error_response(_get_message("cannot_delete"))
        elif self.entity_is_type_with_values(entity_id, entity_type_id):
            self.display_error_response(_get_message("type_has_values"))

        if not self.http_response:
            # Get user to confirm action before actually doing it
            # log.info(
            #     "entity_coll_id %s, type_id %s, entity_id %s, confirmed_action_uri %s"%
            #     (entity_coll_id, entity_type_id, entity_id, confirmed_action_uri)
            #     )
            delete_params = (
                { form_action_field:    ["Delete"]
                , form_value_field:     [entity_id]
                , "completion_url":     [self.get_continuation_here()]
                , "search_for":         [self.request_dict.get('search_for',"")]
                })
            curi = self.get_continuation_url()
            if curi:
                delete_params["continuation_url"] = [curi]
            return (
                self.check_authorization("delete")
                or
                ConfirmView.render_form(self.view.request,
                    action_description=     _get_message("confirm_completion"),
                    action_params=          dict_querydict(delete_params),
                    confirmed_action_uri=   complete_action_uri,
                    cancel_action_uri=      self.get_continuation_here(),
                    title=                  self.view.site_data()["title"]
                    )
                )
        return self.http_response

    # Additonal support functions for list views

    def get_type_list_id(self, type_id):
        """
        Return default list_id for listing defined type, or None
        """
        list_id = None
        if type_id:
            if self.curr_typeinfo.recordtype:
                list_id = extract_entity_id(
                    self.curr_typeinfo.recordtype.get(ANNAL.CURIE.type_list, None)
                    )
            else:
                log.warning("DisplayInfo.get_type_list_id no type data for %s"%(type_id))
        return list_id

    def check_list_id(self, list_id):
        """
        Check for existence of list definition: 
        if it exists, return the supplied list_id, else None.
        """
        if list_id and RecordList.exists(self.collection, list_id, altscope="all"):
            return list_id
        return None

    def get_list_id(self, type_id, list_id):
        """
        Return supplied list_id if defined, otherwise find default list_id for
        entity type or collection (unless an error has been detected).
        """
        if not self.http_response:
            list_id = (
                list_id or 
                self.check_list_id(self.get_type_list_id(type_id)) or
                self.check_list_id(self.collection.get_default_list()) or
                ("Default_list" if type_id else "Default_list_all")
                )
            if not list_id:
                log.warning("get_list_id failure: %s, type_id %s"%(list_id, type_id))
        return list_id

    def get_list_view_id(self):
        return extract_entity_id(
            self.recordlist.get(ANNAL.CURIE.default_view, None) or "Default_view"
            )

    def get_list_type_id(self):
        return extract_entity_id(
            self.recordlist.get(ANNAL.CURIE.default_type, None) or "Default_type"
            )

    # Additional support functions for collection view

    def get_default_view_type_entity(self):
        """
        Return default view_id, type_id and entity_id to display for collection,
        or None for any values not defined.
        """
        view_id, type_id, entity_id = self.collection.get_default_view()
        return (self.check_view_id(view_id), type_id, entity_id)

    # Additonal support functions for entity views

    def check_view_id(self, view_id):
        """
        Check for existence of view definition: 
        if it exists, return the supplied view_id, else None.
        """
        if view_id and RecordView.exists(self.collection, view_id, altscope="all"):
            return view_id
        return None

    def get_view_id(self, type_id, view_id):
        """
        Get view id or suitable default using type if defined.
        """
        if not self.http_response:
            view_id = (
                view_id or 
                self.check_view_id(self.curr_typeinfo.get_default_view_id())
                )
            if not view_id:
                log.warning("get_view_id: %s, type_id %s"%(view_id, self.type_id))
        return view_id

    def entity_exists(self, entity_id, entity_type):
        """
        Test a supplied entity is defined in the current collection,
        returning true or False.

        entity_id           entity id that is to be tested..
        entity_type         type of entity to test.
        """
        typeinfo = self.curr_typeinfo
        if not typeinfo or typeinfo.get_type_id() != entity_type:
            typeinfo = EntityTypeInfo(self.collection, entity_type)
        return typeinfo.entityclass.exists(typeinfo.entityparent, entity_id)

    def entity_is_type_with_values(self, entity_id, entity_type):
        """
        Test if indicated entity is a type with values defined.
        """
        if entity_type == layout.TYPE_TYPEID:
            typeinfo = EntityTypeInfo(
                self.collection, entity_id
                )
            return next(typeinfo.enum_entity_ids(), None) is not None
        return False

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
        # Use default view for entity type
        # (Use list view id only for new entities)
        return self.view.view_uri(
                "AnnalistEntityDefaultDataView", 
                coll_id=coll_id, 
                type_id=type_id,
                entity_id=entity_id,
                action=action
                )
        # return self.view.view_uri(
        #         "AnnalistEntityEditView", 
        #         coll_id=coll_id, 
        #         view_id=self.get_list_view_id(), 
        #         type_id=type_id,
        #         entity_id=entity_id,
        #         action=action
        #         )

    def get_src_entity_resource_url(self, resource_ref):
        """
        Return URL for accessing source entity resource data 
        (not including any view information contained in the current request URL).

        Contains special logic for accessing collection and site metadata
        """
        assert self.coll_id is not None
        assert self.curr_typeinfo is not None
        type_id   = self.curr_typeinfo.get_type_id()
        if type_id == layout.COLL_TYPEID:
            entity_id = self.src_entity_id or layout.SITEDATA_ID
            base_url  = self.view.get_collection_base_url(entity_id)
        else:
            entity_id = self.src_entity_id or "__unknown_src_entity__"
            base_url  = self.view.get_entity_base_url(
                self.coll_id, type_id,
                entity_id
                )
        return urljoin(base_url, resource_ref)

    # Additonal support functions

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
        continuation_here = self.view.continuation_here(
            request_dict=self.request_dict,
            default_cont=self.get_continuation_url(),
            base_here=base_here
            )
        # log.info("DisplayInfo.get_continuation_here: %s"%(continuation_here))
        return continuation_here

    def update_continuation_url(self, 
        old_type_id=None, new_type_id=None, 
        old_entity_id=None, new_entity_id=None
        ):
        """
        Update continuation URI to reflect renamed type or entity.
        """
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

    def get_entity_data_ref(self, name_ext=".jsonld", return_type=None):
        """
        Returns a relative reference (from entity base) for the metadata for the
        current entity using the supplied name extension.
        """
        assert self.curr_typeinfo is not None
        data_ref = self.curr_typeinfo.entityclass.meta_resource_name(name_ext=name_ext)
        # log.info("@@@@ get_entity_data_ref: data_ref "+data_ref)
        data_ref = make_data_ref(
            self.view.get_request_path(),   # For parameter values
            data_ref, 
            return_type
            )
        # log.info("@@@@ get_entity_data_ref: data_ref "+data_ref)
        return data_ref

    def get_entity_jsonld_ref(self, return_type=None):
        """
        Returns a relative reference (from entity base) for the metadata for the
        current entity, to be returned as JSON-LD data.
        """
        jsonld_ref = self.get_entity_data_ref(name_ext=".jsonld", return_type=return_type)
        return jsonld_ref

    def get_entity_jsonld_url(self, return_type=None):
        """
        Returns a string that can be used as a reference to the entity metadata resource,
        optionally with a specified type parameter added.

        Extracts appropriate local reference, and combines with entity URL path.
        """
        data_ref = self.get_entity_jsonld_ref(return_type=return_type)
        data_url = self.get_src_entity_resource_url(data_ref)
        log.debug(
            "get_entity_jsonld_url: _entityfile %s, data_ref %s, data_url %s"%
            (self.curr_typeinfo.entityclass._entityfile, data_ref, data_url)
            )
        return data_url

    def get_entity_turtle_ref(self, return_type=None):
        """
        Returns a relative reference (from entity base) for the metadata for the
        current entity, to be returned as Turtle data.
        """
        turtle_ref = self.get_entity_data_ref(name_ext=".ttl", return_type=return_type)
        return turtle_ref

    def get_entity_turtle_url(self, return_type=None):
        """
        Returns a string that can be used as a reference to the entity metadata resource,
        optionally with a specified type parameter added.

        Extracts appropriate local reference, and combines with entity URL path.
        """
        turtle_ref = self.get_entity_turtle_ref(return_type=return_type)
        turtle_url = self.get_src_entity_resource_url(turtle_ref)
        log.debug(
            "get_entity_turtle_url: _entityfile %s, turtle_ref %s, turtle_url %s"%
            (self.curr_typeinfo.entityclass._entityfile, turtle_ref, turtle_url)
            )
        return turtle_url

    def get_entity_list_ref(self, list_name=layout.ENTITY_LIST_FILE, return_type=None):
        """
        Returns a string that can be used as a reference to the entity list data
        relative to the current list URL.
        """
        return make_data_ref(
            self.view.get_request_path(), 
            list_name, 
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

        Context values set here do not need to be named in the valuye map used to
        create the view context.
        """
        site_url_parts = urlsplit(self.site._entityurl)
        context = (
            { 'site_label':         self.sitedata["title"]
            , 'title':              self.sitedata["title"]
            , 'heading':            self.sitedata["title"]
            , 'action':             self.action
            , 'coll_id':            self.coll_id
            , 'type_id':            self.type_id
            , 'view_id':            self.view_id
            , 'list_id':            self.list_id
            , 'collection':         self.collection
            , 'info_coll_id':       self.coll_id or layout.SITEDATA_ID
            , "SITE":               site_url_parts.path
            , "HOST":               self.reqhost            
            })
        context.update(self.authorizations)
        if self.collection:
            coll_url_parts = urlsplit(self.collection._entityurl)
            context.update(
                { 'heading':    self.collection[RDFS.CURIE.label]
                , 'coll_label': self.collection[RDFS.CURIE.label]
                , "COLL":       coll_url_parts.path
                , "BASE":       coll_url_parts.path + layout.COLL_BASE_REF
                , "PAGE":       coll_url_parts.path + layout.COLL_PAGE_REF
                })
            context['title'] = "%(coll_label)s"%context
        if self.recordview:
            context.update(
                { 'heading':            self.recordview[RDFS.CURIE.label]
                , 'view_label':         self.recordview[RDFS.CURIE.label]
                , 'edit_view_button':   self.recordview.get(ANNAL.CURIE.open_view, "yes")
                })
            context['title'] = "%(view_label)s - %(coll_label)s"%context
            task_buttons      = self.recordview.get(ANNAL.CURIE.task_buttons, None)
            edit_task_buttons = self.recordview.get(ANNAL.CURIE.edit_task_buttons, task_buttons)
            view_task_buttons = self.recordview.get(ANNAL.CURIE.view_task_buttons, task_buttons)
            self.add_task_button_context('edit_task_buttons', edit_task_buttons, context)
            self.add_task_button_context('view_task_buttons', view_task_buttons, context)
        if self.recordlist:
            context.update(
                { 'heading':                self.recordlist[RDFS.CURIE.label]
                , 'list_label':             self.recordlist[RDFS.CURIE.label]
                , 'entity_list_ref':        self.get_entity_list_ref()
                , 'entity_list_ref_json':   self.get_entity_list_ref(return_type="application/json")
                , 'entity_list_ref_turtle': self.get_entity_list_ref(list_name=layout.ENTITY_LIST_TURTLE)
                })
            context['title'] = "%(list_label)s - %(coll_label)s"%context
        if self.curr_typeinfo:
            context.update(
                { 'entity_data_ref':        self.get_entity_jsonld_url()
                , 'entity_data_ref_json':   self.get_entity_jsonld_url(return_type="application/json")
                , 'entity_turtle_ref':      self.get_entity_turtle_url()
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
        if self.info_messages:
            context.update(
                { "info_head":      message.ACTION_COMPLETED
                , "info_message":   "\n".join(self.info_messages)
                })
        if self.error_messages:
            context.update(
                { "error_head":     message.DATA_ERROR
                , "error_message":  "\n".join(self.error_messages)
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
