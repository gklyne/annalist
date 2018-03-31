"""
Defines Annalist built-in identifier values (URIs)
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

class Urispace(object):
    """
    Placeholder class for URI values in namespace.
    """
    def __init__(self):
        return

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
        self.URI      = Urispace()
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

    def __getattr__(self, name):
        """
        Return value for <namespace>.<name>
        """
        # Called for attributes that aren't defined.
        # Placeholder should generate error
        return self.__dict__[name]

def makeNamespace(prefix, baseUri, names):
    """
    Create a namespace with given prefix, base URI and set of local names.

    Returns the namespace value.  Attributes of the URI attribute are URIs for
    the corresponding identifier (e.g. ANNAL.URI.Site, cf. below).  Attributes of
    the CURIE attribute are CURIES (e.g. ANNAL.CURIE.Site).
    """
    ns = Namespace(prefix, baseUri)
    for name in names:
        setattr(ns.URI,   name, ns.mk_uri(name))
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
    [ "Unknown_type"
    # Entity value types
    , "Collection"
    , "Default_type"
    , "Entity"
    , "EntityData"
    , "EntityRoot"
    , "Enum"
    , "Enum_field_placement"
    , "Enum_list_type"
    , "Enum_render_type"
    , "Enum_value_mode"
    , "Enum_value_type" # Unused??
    , "Field"
    , "Field_group"
    , "List"
    , "Site"
    , "SiteData"
    , "Type"
    , "Type_Data"
    , "User"
    , "View"
    , "Vocabulary"
    # Repeat/list group types
    , "Field_list"
    , "Field_superproperty_uri"
    , "Group_field" # @@deprecated
    , "List_field"
    , "Type_supertype_uri"
    , "View_field"
    # Data value and resource types
    , "Audio"
    , "EntityRef"
    , "Identifier"
    , "Image"
    , "Longtext"
    , "Metadata"
    , "Placement"
    , "Resource"
    , "Richtext"
    , "Text"
    , "Video"
    # Properties in list JSON
    , "entity_list"
    # Properties in internal entities
    , "id", "type_id", "type", "url", "uri"
    # Types, Views, lists and field groups
    , "default_type", "default_view"
    , "supertype_uri"
    , "display_type", "type_list", "type_view"
    , "field_aliases", "alias_target", "alias_source"
    , "view_entity_type", "open_view", "view_fields"
    , "task_buttons", "edit_task_buttons", "view_task_buttons"
    , "button_id", "button_label", "button_help"
    , "list_entity_type", "list_entity_selector", "list_fields"
    , "group_entity_type", "group_fields"
    , "field_id"
    # User permissions
    , "user_uri", "user_permission"
    # Field definitions
    , "field_render_type", "field_value_type", "field_value_mode"
    , "field_entity_type"
    , "placeholder", "tooltip", "default_value", "property_uri"
    , "superproperty_uri"
    , "field_ref_type", "field_ref_restriction", "field_ref_field"
    , "field_fields", "repeat_label_add", "repeat_label_delete" 
    , "field_name", "field_placement"
    , "group_ref" # deprecated
    # Collection metadata
    , "software_version", "meta_comment", "inherit_from"
    , "default_list"
    , "default_view_id", "default_view_type", "default_view_entity"
    # Schema properties (like RDF equivalents, but connecting Annalist entities)
    # The intent is that the RDF equivalents can be inferred by looking at the 
    # referenced entities.
    , "subclassOf", "subpropertyOf", "domain", "range"
    # Deprecated identifiers - used in entity migration
    , "Slug", "RepeatGroup", "RepeatGroupRow" 
    , "options_typeref", "restrict_values", "target_field"
    , "record_type", "field_target_type", "comment"
    , "supertype_uris"
    , "user_permissions"
    ])

# End.
