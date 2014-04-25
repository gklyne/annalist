# Notes for data-driven form rendering and entity update from form submission.

There are three types of data structure involved in form-based record/entity editing:

1. Stored entity data.  This is a decoded JSON data structure, with object keys that are URIs or CURIEs.
2. View rendering context.  This is used by the Django template view renderer, and potentially by other template-based rendering tools, to supply data to be incorporated in a rendered HTML page (or potentially some other rendered format).  Dictionary keys are simple names, but values may be dictionaries, lists or arbitrary Python objects - see Django template variable description for details.
3. HTML form field values.  A flat dictionary of simple name/value pairs.

The process of presenting amnd processing a form for editing an entity goes as follows:
* get entity data
* map entity data into a Django context
* Django template uses context data to render field data in an HTML form
* When form is submitted, map form field data back to entity data fot storage.
* When a form has to be redisplayed, map the form field data back to a Django context for re-rendering the form, possibly with additional values and/or messages.  This may be done directly, or indirectly via mapping to entity data and then mapping back to context data.


    Entity/<other>      -> Context -> Form -> Entity

    <title>             -> title            -> title           
    <coll_id>           -> coll_id          -> coll_id         
    <type_id>           -> type_id          -> type_id         
    <action>            -> action           -> action          
    <continuation_uri>  -> continuation_uri -> continuation_uri

    annal:id            -> entity_id        -> entity_id     
    annal:type          -> entity_type      -> entity_type   
    rdfs:label          -> entity_label     -> entity_label  
    rdfs:comment        -> entity_comment   -> entity_comment
    annal:id            -> orig_id          -> orig_id       
    annal:type          -> orig_type        -> orig_type     

Fields in a view description are processed as described below.
Keys `entity_id` and `entity_type` are special cases, as they are used to form the name of a saved entity and, as such, are recognized specially by the form rendering and response handling code.  Other keys are treated without interpretation. (?)

The examples that follow are for (simplified) display and editing of a record view description.  As such, they are somewhat confusingly self-referential as the data partially describes its own rendering.


# Entity

This is raw stored data.

    { "@id":                "annal:display/RecordView_view"
    , "annal:id":           "RecordView_view"
    , "annal:type":         "annal:Record_view"
    , "annal:record_type":  "annal:RecordView"
    , "rdfs:label":         "View description for record view description"
    , "rdfs:comment":       "This resource describes the form that is used when displaying and/or editing a record view description"
    , "annal:view_fields":
      [ { "annal:field_id":         "View_id"
        , "annal:field_placement":  "small:0,12;medium:0,6"
        }
      , { "annal:field_id":         "View_label"
        , "annal:field_placement":  "small:0,12"
        }
      , { "annal:field_id":         "View_comment"
        , "annal:field_placement":  "small:0,12"
        }
      , { "annal:repeat_id":            "View_fields"
        , "annal:repeat_label":         "Record fields"
        , "annal:repeat_btn_label":     "field"
        , "annal:repeat_for_values":    "annal:view_fields"
        // If repeated values refer to an entity from which values are accessed, give type and field with id
        // These are used to create bound field values in the generated context structure
        , "annal:repeat_entity_type":   "_field"
        , "annal:repeat_entity_id":     "annal:field_id"
        , "annal:repeat":
          [ { "annal:field_id":             "Field_id"
            , "annal:field_placement":      "small:0,12; medium:0,6"
            }
          , { "annal:field_id":             "Field_placement"
            , "annal:field_placement":      "small:0,12; medium:6,6"
            }
          ]
        }
      ]
    }


# Context

The context is created by combining stored data with a view description.  Some context values are evaluated on the fly from combinations of entities and view/field descriptions, etc.  The mapping classes take care of these constructions.


    "title":                <title>
    "coll_id":              <coll_id>
    "type_id":              <type_id>
    "view_id":              <view_id>
    "action":               <action>
    "continuation_uri":     <continuation_uri>

    "entity_id":            "RecordView_view"
    "entity_uri":           "annal:display/RecordView_view"
    "entity_type":          "annal:RecordView"
    "entity_label":         "View description for record view description"
    "entity_comment":       "This resource describes the form ..."
    "orig_id":              "RecordView_view"
    "orig_type":            "annal:RecordView"

    "fields":
        0:  FieldValueMap(
              c="fields", 
              f=FieldDescription(
                  { "annal:field_id":        "View_id"
                  , "annal:field_placement": "small:0,12; medium:0,6"
                  })
              )
        1:  FieldValueMap(
              c="fields", 
              f=FieldDescription(
                  { "annal:field_id":        "View_label"
                  , "annal:field_placement": "small:0,12"
                  })
              )
        2:  FieldValueMap(
              c="fields", 
              f=FieldDescription(
                  { "annal:field_id":        "View_comment"
                  , "annal:field_placement": "small:0,12"
                  })
              )
        3:  RepeatValuesMap(
              c="repeat",
              e="annal:view_fields",    // repeat for values of entity field
              f=EntityFieldMap(
                  type="_field",
                  id_field="field_id",
                  fields=(
                      [ FieldDescription(
                          { "annal:field_id":        "Field_id"
                          , "annal:field_placement": "small:0,12; medium:0,6"
                          })
                      , FieldDescription(
                          { "annal:field_id":        "Field_placement"
                          , "annal:field_placement": "small:0,12; medium:6,6"
                          })
                      ])
                  ),
              r=RepeatDescription(
                  { 'annal:repeat_id':        "View_fields"     // ID for this repeat group
                  , 'annal:repeat_label':     "Record fields"   // Label for this repeat group
                  , 'annal:repeat_btn_label': "field"           // Button label for add/remove buttons
                  })
              )


# Form data

Note this is a flat identifier space, so repetition must be converted to generated identifiers.  Form data is generated through the view template.  Sufficient information must be provided to allow for reconstruction of the stored entity value when a form response is posted.  Each top-level field is assumed to have a unique name.

    # Information from hidden fields
    "orig_id":              "RecordView_view"
    "orig_type":            "annal:RecordView"
    "view_id":              <view_id>
    "action":               <action>
    "continuation_uri":     <continuation_uri>

    # Generated from field descriptions
    "View_id":              ...
    "View_label":           ...
    "View_comment":         ...

    # Generated from repeat field group description
    "repeat_View_fields__Field_id":         ... value for "Field_id"
    "repeat_View_fields__Field_placement":  ... value for "Field_placement"


# Required to implement

* `FieldDescription` - object describing a field, and methods to perform manipulations.
  (part done in entityeditbase.get_field_context)
  - Done.
* `RepeatDescription` - object describing a repeated values group, and methods to perform manipulations.
  (part done in entityeditbase.get_repeat_context; maybe to be subsumed by RepeatValuesMap?)
* `SimpleValueMap` - a direct mapping between an entity field, a context field and a form field.
* `FieldValueMap` - an indirect mapping between an entity field, a context field and a form field, controlled by field description data (cf. FieldDescription)  Implemented, but update to use FieldDescription values.
* `EntityFieldMap` - try to replace existing ad-hoc logic for dealing with field mapping.  
  Compared with GroupRepeatMap, the entity selection is explicit.
  This could be suitable to replace GroupRepeatMap.
* `RepeatValuesMap` - this describes a group of repeated fields.

The value map objects are constructed to take account of a particular view description, and all support the following methods:

* `map_entity_to_context(context, entity_values, extras={})` - maps entity values, usually augmented by entity-independent "extras" values, adding the resulting values to the supplied `context` dictionary.  The form of expected entity_values may be constrained by the particular value mapping class used.
* `map_form_to_entity(values, form_data)` - maps form data to entity value fields, which are added to or replaced in the supplied `values` dictionary.
* `map_form_to_context(values, form_data, extras={})`



