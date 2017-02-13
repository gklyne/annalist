"""
Defines Annalist built-in identifier values (URIs)
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

class Curiespace(object):
    """
    Placeholder class for CURIE values in namespace.
    """
    def __init__(self):
        return


class Namespace(object):
    """
    Class represents namespace of URI identifiers.

    Provides expressions for URI and CURIE values of each identifier in the namespace.

    >>> ns = Namespace("test", "http://example.com/test/")
    >>> cf = ns.mk_curie("foo")
    >>> cf
    'test:foo'
    >>> uf = ns.mk_uri("foo")
    >>> uf
    'http://example.com/test/foo'
    >>> ns.to_uri(cf)
    'http://example.com/test/foo'
    >>> ns.to_uri("notest:bar")
    'notest:bar'
    """

    def __init__(self, prefix, baseUri):
        """
        Initialise a namespace.

        prefix      a CURIE prefix to be associated with this namespace.
        _baseUri    a base URI for all names in this namespace
        """
        self._prefix  = prefix
        self._baseUri = baseUri
        self.CURIE    = Curiespace()
        return

    def mk_curie(self, name):
        """
        Make a CURIE string for an identifier in this namespace
        """
        return self._prefix+":"+name

    def mk_uri(self, name):
        """
        Make a URI string for an identifier in this namespace
        """
        return self._baseUri+name

    def to_uri(self, curie):
        """
        Converts a supplied CURIE to a URI if it uses the current namespace prefix.
        """
        parts = curie.split(':', 1)
        if (len(parts) == 2) and (parts[0] == self._prefix):
            return self.mk_uri(parts[1])
        return curie

def makeNamespace(prefix, baseUri, names):
    """
    Create a namespace with given prefix, base URI and set of local names.

    Returns the namespace value.  Attributes of the namespace value are URIs
    for the corresponding identifier (e.g. ANNAL.Site, cf. below).  Attributes of
    the CURIE attribute are CURIES (e.g. ANNAL.CURIE.Site).
    """
    ns = Namespace(prefix, baseUri)
    for name in names:
        setattr(ns, name, ns.mk_uri(name))
        setattr(ns.CURIE, name, ns.mk_curie(name))
    return ns

"""
Partial enumeration of RDF namespace - add others as needed
"""
RDF = makeNamespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    [ "Property", "Statement", "List"
    , "type", "value"
    , "first", "rest", "nil"
    ])

"""
Partial enumeration of RDFS namespace - add others as needed
"""
RDFS = makeNamespace("rdfs", "http://www.w3.org/2000/01/rdf-schema#",
    [ "Resource", "Class", "Literal", "Container", "Datatype"
    , "label", "comment", "member", "seeAlso"
    ])

"""
Partial enumeration of OWL namespace
"""
OWL = makeNamespace("owl", "http://www.w3.org/2002/07/owl#",
    [ "Thing", "Nothing"
    , "sameAs", "differentFrom", "equivalentClass"
    ])

"""
Annalist namespace terms
"""
ANNAL = makeNamespace("annal", "http://purl.org/annalist/2014/#",
    [ "EntityRoot", "Entity", "EntityData"
    , "Site", "SiteData", "Collection"
    # Internal IDs for MIME types (see resourcetypes.py)
    , "Metadata", "Type_Data"
    # Entity types
    , "User", "Type", "List", "View", "Field_group", "Field", "Enum"
    , "Enum_field_placement", "Enum_list_type", "Enum_render_type", "Enum_value_mode", "Enum_value_type"
    # Group value types
    , "View_field", "List_field", "Group_field"
    # Value types
    , "Text", "Longtext", "Richtext", "EntityRef", "Identifier"
    , "Placement", "Image", "Audio", "Vocabulary"
    , "Resource"
    , "Default_type", "Unknown_type"
    # Properties in list JSON
    , "entity_list"
    # Properties in internal entities
    , "id", "type_id", "type"
    , "url", "uri", "record_type"
    # Types, Views, lists and field groups
    , "default_type", "default_view"
    , "supertype_uri"
    , "display_type", "type_list", "type_view"
    , "field_aliases", "alias_target", "alias_source"
    , "open_view", "view_fields"
    , "edit_task_buttons", "view_task_buttons"
    , "button_id", "button_label", "button_help"
    , "list_entity_selector", "list_fields"
    , "group_fields"
    , "field_id"
    # Enumerated value terms
    # , "enum_uri"
    # User permissions
    , "user_uri", "user_permission"
    # Field definitions
    , "field_render_type", "field_value_type", "field_value_mode"
    , "field_entity_type"
    , "placeholder", "default_value", "property_uri"
    , "field_ref_type", "field_ref_restriction", "field_ref_field"
    , "group_ref", "repeat_label_add", "repeat_label_delete"
    , "field_name", "field_placement"
    # Collection metadata
    , "software_version", "meta_comment", "inherit_from"
    , "default_list"
    , "default_view_id", "default_view_type", "default_view_entity"
    # Deprecated properties - used in entity migration tables
    , "Slug", "RepeatGroup", "RepeatGroupRow" 
    , "options_typeref", "restrict_values", "target_field"
    , "field_target_type", "comment"
    , "supertype_uris"
    , "user_permissions"
    ])

# End.
