# Annalist resources and representations

Metadata: provenance, access control, ...?

Could collection/record be Atom feed/entry?


# Collection

Collection service document (cacheable):

    an:access _accessRef_ ;             # exactly 1
    an:query _queryRef_ ;               # exactly 1
    an:metadata _metaRef_ ;             # exactly 1
    an:defaultView _listRef_ ;          # exactly 1
    an:listView _listRef_ ;             # 1..
    an:recordView _viewRef_ ;           # 0..
    an:recordType _typeRef_ ;           # 0..
    .

# Metadata, collected and managed by system; not user-editable:

    view template
    creator
    creation data
    modification (who, when)
    (other provenance?)


# Record (frame)

    an:access _accessRef_ ;             # 0..1
    an:metadata _metaRef_ ;             # 1..1
    an:defaultView _viewRef_ ;          # 1..1 ??
    an:recordType _typeRef_ ;           # 0..   (or rdf:type?)
    an:fieldRef _ref_ ;                 # 0..   (actual properties are subproperties)
    an:fieldVal _val_ ;                 # 0..   (actual properties are subproperties)
    .


# Attachment (blob)

(Dereferencing returns the blob of whatever type.  I think this is subsumed by Record fields.)

How to add a blob to a collection; need to distinguish from records?  Use separate blob-store URI?  Access control?


# Views

## List view

Parameterized by collection

List view:

    a an:ListView, an:Record ;
    an:viewRows  _rowcount_ ;           # 0..1
    an:viewWidth _widthId_ ;            # 0..1
    an:viewSelector ??? ;               # 1..1
    an:listField                        # 1..
      [ an:fieldProperty _propUri_ ; an:listFieldPos _posId_ ] ;
    an:searchService _UriTemplate_ ;    # 0..1

Grid view:

    a an:GridView, an:Record ;
    an:viewRows  _rowcount_ ;           # 0..1
    an:viewWidth _widthId_ ;            # 0..1
    an:cellWidth _widthId_ ;            # 0..1
    an:viewSelector ??? ;               # 1..1
    an:searchService _UriTemplate_ ;    # 0..1
    an:gridField                        # 1..
      [ an:fieldProperty _propUri_ ; an:gridFieldPos _posId_ ] ;


## Record view

Parameterized by record


# Access control

    a an:AccessDefinition ;
    an:authorize _UriTemplate_ ;        # exactly 1 with {collection}, {userid}, {operation} {source}

    authorization: collection -> (userid, operation, source) -> obligation

userid is determined separately by an authentication service (e.g.openid) which is invoked by the initial HTTP request handler.

operation is "GET", "HEAD", "PUT", "POST" or "DELETE".

source is the source of the request (IP address or other key.

obligation is the URI for a service that returns a permission or a reason string, possibly after further interaction with the user.

    obligation:  IO( Either Permission String )

Three obligation cases initially:

    return "Access denied"
    
    return Permission (allow), 

    { ok <- (agree t&c) 
    ; if ok (return permission) (return "Must accept t&c to perform operation")
    }

the permission returned is the URI template for a service invoked by the actual operation that confirms the authorized conditions match what is requested to do.  The result from invoking the permission service is checked by the logic that performs the operation (the PEP).

    permission: collection -> (userid, operation, source) -> IO(boolean)

Oauth.  The above flow appears to be very similar to what is provided by Oauth2, so it would probably make sense to try and use that.  Authentication will need to be handled separately.  Also look out for potential security problems, and make use HTTP is used for token exchanges (cf. http://hueniverse.com/2012/07/oauth-2-0-and-the-road-to-hell/, http://hueniverse.com/oauth/) 

https://github.com/litl/rauth seems to be the favoured Python implementation of Oauth 2 (and 1?)

I thought about roles as part of the interface, but feel these are part of the administrative aspects of authorization, not needed to be part of the access control mechanism seen by an application.

Should an authorization request return alternate possible obligations?  If so, there should be some way to learn about their differences


# (Queries: by type, property/value, keyword, sparql, owl)

    a an:QueryDescription 
    an:queryByType _UriTemplate_ ;      # exactly 1 with {type}
    an:queryByProp _UriTemplate_ ;      # 0..1 with {prop} {val}
    an:queryByKeyword _UriTemplate_ ;   # 0..1
    an:queryBySparql _sparqlSdRef_ ;    # 0.. (see SPARQL service description; convention for collection?)
    an:quertByOwl _owlSdRef_ ;          # 0.. (model on SPARQL SD?)
    .

