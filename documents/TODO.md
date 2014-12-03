# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# V0.1.7, towards V0.1.8

- [x] Add button to annalist.net page: https://github.com/BetaNYC/getDataButton
- [x] Extend form-generator capabilities [issue #2](https://github.com/gklyne/annalist/issues/2)
    - [x] Revise representation of repeat field structures in view description: repeat description to be part of root of repeat structure, not an ad ho0c field at the end.  This should remove some special cases from the code.
    - [x] Refactor handling of repeat field groups
    - [x] Define type for field group (_group?  Or use _view?)
    - [x] Use _list rather than _view? (no: list has much more bound-in semantics)
    - [x] Rename 'View_field' to (say) 'View_field_view' (cf. previous use _list)
    - [x] Define view for field group (list of fields)
    - [?] Define list for field group
    - [x] Redefine view with list of fields?  Not if that impacts usability.
    - [x] Define e-v-map for defined list of fields
    - [x] Repeat to reference list of fields 
- [x] Eliminate duplication with list view - rework list to use same repeating mechanism as view
- [ ] Provide clean mechanism to propagate extra context to bound fields in repeat group rendering
- [ ] Use distinguished names for internally-generated context keys (e.g. '_fields')
- [ ] Simplify template now that repat fields are handled by a field renderer
- [x] Try to make mapping classes more consistent in their return types for sub-context values
- [ ] Try eliminating `view_context` parameter from `FieldListValueMap` constructor - it appears to be unused (or is it... used for generating enumerated type lists?)
- [ ] Add field for `annal:field_entity_type` property in field view
- [ ] Add/test option to add repeated field group
- [ ] Revisit definitions for BibJSON view
- [ ] Consider use of "hidden" flags on views, types, fields, etc. to avoid cluttering UI with internal details?  (defer?)
- [ ] Think about fields that return subgraph (defer?)
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.

(sub-release?)

- [ ] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [ ] Blob and file upload support: images, spreadsheets, ...
    - [ ] Field type to link to uploaded file
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] Shared deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [ ] Figure out how to preserve defined users when reinstalling the software.
    - I think it is because the Django sqlite database file is replaced.  Arranging for per-configuration database files (per above) might alleviate this.
- [ ] `annalist-manager` help to provide list of permission tokens
- [ ] Automated test suite for annalist_manager
    - [ ] annalist-manager initialize [ CONFIG ]
    - [ ] annalist-manager createadminuser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager updateadminuser [ username ] [ CONFIG ]
    - [ ] annalist-manager setdefaultpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager setpublicpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager deleteuser [ username ] [ CONFIG ]
    - [ ] annalist-manager createsitedata [ CONFIG ]
    - [ ] annalist-manager updatesitedata [ CONFIG ]
- [ ] 'New' and 'Copy' from list view should bring up new form with id field selected, so that typing a new value replaces the auto-generated ID.
- [ ] 'Add field' can't be followed by 'New field' because of duplicate property used
- [ ] Easy way to view log; from command line (via annalist-manager); from web site (link somewhere)
    - [x] annalist-manager serverlog command returns log file name
    - [ ] site link to view log
- [ ] Usability issues arising from creating cruising log
    - [ ] Want option to create linked record directly from other record entry field (issue #??).
    - [ ] Fields should default to previous value entered.  How to save these?

(sub-release?)

- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Review concurrent access issues; document assumptions
- [ ] Use site/collection data to populate help panes on displays; use Markdown.
- [ ] review use of template files vs. use of inline template text in class
    - [x] Need to support edit/view/item/head (NOT: probably via class inheritance structure)
    - [x] Inline template text should be more efficient as it avoids repeated reading of template files
    - [x] Inline template text keeps value mapping logic with template logic
    - [ ] Inline templates may be harder to style effectively; maybe read HTML from file on first use?
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s). 
- [ ] Provide content for the links in the page footer

Notes for Future TODOs:

- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of type definitions
- [ ] Make default values smarter; e.g. field renderer logioc to scan collection data for candidates?
- [ ] Option to rearrange fields on view form (after restructuring?)
- [ ] When creating type, default URI to be based on id entered
- [ ] Allow type definition to include template for new id, e.g. based on current date
- [ ] Use local prefix for type URI (when prefixes are handled properly); e.g. coll:Type/<id>
- [ ] Associate a prefix with a collection? 
- [ ] Provide a way to edit collection metadata (e.g. link from Customize page)
- [ ] Provide a way to edit site metadata (e.g. via link from site front page)
- [ ] Provide a way to view/edit site user permissions (e.g. via link from site front page)
- [ ] Provide a way to view/edit site type/view/list/etc descriptions (e.g. via link from site front page)
- [ ] Undefined list error display (any error?) - include link to collection in top bar
- [ ] Help display for view: use commentary text from view descrtiption; thus can tailore help for each view.
- [ ] Introduce markdown rendering type
- [ ] Use markdown directly for help text
- [ ] Consider associating property URI with view rather than/as well as field, so fields can be re-used
- [ ] Option to auto-generate unique property URI for field in view, maybe using field definition as base
- [ ] Need easier way to make new entries for fields that are referenced from a record; e.g. a `New value` button as part of an enum field.
- [ ] Instead of separate link on the login page, have "Local" as a login service option.
- [ ] Entity edit view: "New field" -> "New field type"


# Repeated field reprentation:

## Current

View description

```
{ "@id":                "annal:display/View_view"
, "@type":              ["annal:View"]
, "annal:id":           "View_view"
, "annal:type_id":      "_view"
, "annal:uri":          "annal:display/View_view"
, "annal:record_type":  "annal:View"
, "rdfs:label":         "View description for record view description"
, "rdfs:comment":       "This resource describes the form that is used when displaying and/or editing a record view description"
, "annal:add_field":    "no"
, "annal:view_fields":
  [ { "annal:field_id":               "View_id"
    , "annal:field_placement":        "small:0,12;medium:0,6"
    }
  , { "annal:field_id":               "View_label"
    , "annal:field_placement":        "small:0,12"
    }
  , { "annal:field_id":               "View_comment"
    , "annal:field_placement":        "small:0,12"
    }
  , { "annal:field_id":               "View_target_type"
    , "annal:field_placement":        "small:0,12"
    }
  , { "annal:field_id":               "View_add_field"
    , "annal:field_placement":        "small:0,12;medium:0,6"
    }
  , { "annal:repeat_id":              "View_fields"
    , "annal:repeat_label":           "Fields"
    , "annal:repeat_label_add":       "Add field"
    , "annal:repeat_label_delete":    "Remove selected field(s)"
    , "annal:repeat_entity_values":   "annal:view_fields"
    , "annal:repeat_context_values":  "repeat"
    , "annal:repeat":
      [ { "annal:field_id":               "Field_sel"
        , "annal:field_placement":        "small:0,12; medium:0,6"
        }
      , { "annal:field_id":               "Field_placement"
        , "annal:field_placement":        "small:0,12; medium:6,6"
        }
      ]
    }
  ]
}
```

Default_view description:

```
{ "@id":                "./"
, "@type":              ["annal:View"]
, "annal:id":           "Default_view"
, "annal:type_id":      "_view"
, "annal:uri":          "annal:display/Default_view"
, "rdfs:label":         "Default record view"
, "rdfs:comment":       "Default record view, applied when no view is specified when creating a record."
, "annal:record_type":  ""
, "annal:add_field":    "yes"
, "annal:view_fields":
  [ { "annal:field_id":         "Entity_id"
    , "annal:field_placement":  "small:0,12;medium:0,6"
    }
  , { "annal:field_id":         "Entity_type"
    , "annal:field_placement":  "small:0,12;medium:6,6right"
    }
  , { "annal:field_id":         "Entity_label"
    , "annal:field_placement":  "small:0,12"
    }
  , { "annal:field_id":         "Entity_comment"
    , "annal:field_placement":  "small:0,12"
    }
  ]
}
```

## Revised

View description

The field descriptions here have a uniform format.  The definition of 
the repeated field descriptions is pushed down into a field description.

```
{ "@id":                "annal:display/View_view"
, "@type":              ["annal:View"]
, "annal:id":           "View_view"
, "annal:type_id":      "_view"
, "annal:uri":          "annal:display/View_view"
, "annal:record_type":  "annal:View"
, "rdfs:label":         "View description for record view description"
, "rdfs:comment":       "This resource describes the form that is used when displaying and/or editing a record view description"
, "annal:add_field":    "no"
, "annal:view_fields":
  [ { "annal:field_id":               "View_id"
    , "annal:field_placement":        "small:0,12;medium:0,6"
    }
  , { "annal:field_id":               "View_label"
    , "annal:field_placement":        "small:0,12"
    }
  , { "annal:field_id":               "View_comment"
    , "annal:field_placement":        "small:0,12"
    }
  , { "annal:field_id":               "View_target_type"
    , "annal:field_placement":        "small:0,12"
    }
  , { "annal:field_id":               "View_repeat_fields"}
    , "annal:field_placement":        "small:0,12"
    }
  ]
}
```

Repeated view-fields description:

```
{ "@id":                        "annal:fields/View_repeat_fields"
, "@type":                      ["annal:Field"]
, "annal:id":                   "View_repeat_fields"
, "annal:type_id":              "_field"
, "rdfs:label":                 "Fields"
, "rdfs:comment":               "This resource describes the repeated field description used when displaying and/or editing a record view description"
, "annal:field_render_type":    "Repeat"
, "annal:field_value_type":     "annal:List"
, "annal:placeholder":          "(repeat field description)"
, "annal:property_uri":         "annal:view_fields"
  # Type of entity that may contain field (omit for any type)
, "annal:field_entity_type":    "annal:View"
  # Reference to description of repeated field
, "annal:view_ref":             "View_field_description"
, "annal:repeat_label_add":     "Add field"
, "annal:repeat_label_delete":  "Remove selected field(s)"
# , "annal:add_field_sentinel":   "annal:add_field"
}
```

Single view-field description (stored as view):

```
{ "@id":                "annal:display/View_field_desc"
, "@type":              ["annal:View"]
, "annal:id":           "View_field_desc"
, "annal:type_id":      "_view"
, "annal:uri":          "annal:display/View_field_desc"
, "annal:record_type":  "annal:Field_desc"
, "rdfs:label":                 "View field description"
, "rdfs:comment":               "This resource describes a single field description used when displaying and/or editing a record view description"
, "annal:add_field":    "no"
, "annal:view_fields":
  [ { "annal:field_id":             "Field_sel"
    , "annal:field_uri":            "annal:field_id"
    , "annal:field_placement":      "small:0,12; medium:0,4"
    }
  , { "annal:field_id":             "Field_uri"
    , "annal:field_uri":            "annal:field_uri"
    , "annal:field_placement":      "small:0,12; medium:4,4"
    }
  , { "annal:field_id":             "Field_placement"
    , "annal:field_uri":            "annal:field_placement"
    , "annal:field_placement":      "small:0,12; medium:8,4"
    }
  ]
}
```


Default_view description:

```
{ "@id":                "./"
, "@type":              ["annal:View"]
, "annal:id":           "Default_view"
, "annal:type_id":      "_view"
, "annal:uri":          "annal:display/Default_view"
, "rdfs:label":         "Default record view"
, "rdfs:comment":       "Default record view, applied when no view is specified when creating a record."
, "annal:record_type":  ""
, "annal:add_field":    "yes"
, "annal:view_fields":
  [ { "annal:field_id":         "Entity_id"
    , "annal:field_placement":  "small:0,12;medium:0,6"
    }
  , { "annal:field_id":         "Entity_type"
    , "annal:field_placement":  "small:0,12;medium:6,6right"
    }
  , { "annal:field_id":         "Entity_label"
    , "annal:field_placement":  "small:0,12"
    }
  , { "annal:field_id":         "Entity_comment"
    , "annal:field_placement":  "small:0,12"
    }
  ]
}
```


