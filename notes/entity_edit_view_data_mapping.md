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



# Field description example

## Entity

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


## Context

The context is created by combining stored data with a view description.  Some context values are evaluated on the fly from combinations of entities and view/field descriptions, etc.  The mapping classes take care of these constructions.


    "title":                <title>
    "coll_id":              <coll_id>
    "type_id":              <type_id>
    "view_id":              <view_id>
    "action":               <action>
    "continuation_uri":     <continuation_uri>

    "entity_id":            "RecordView_view"
    "entity_uri":           "annal:display/RecordView_view"
    "entity_type":          "_view"
    "entity_label":         "View description for record view description"
    "entity_comment":       "This resource describes the form ..."
    "orig_id":              "RecordView_view"
    "orig_type":            "_view"

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
              f=FieldListValueMap(
                  // type="_field",
                  // id_field="field_id",
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

## Form data

Note this is a flat identifier space, so repetition must be converted to generated identifiers.  Form data is generated through the view template.  Sufficient information must be provided to allow for reconstruction of the stored entity value when a form response is posted.  Each top-level field is assumed to have a unique name.

    # Information from hidden fields
    "orig_id":              "RecordView_view"
    "orig_type":            "annal:RecordView"
    "view_id":              "RecordView_view"
    "action":               <action>
    "continuation_uri":     <continuation_uri>

    # Generated from field descriptions
    "entity_id":            "RecordView_view"
    "View_label":           "View description for record view description"
    "View_comment":         "This resource describes the form that is used when displaying and/or editing a record view description"

    # Generated from repeat field group description
    "View_fields__0__Field_id":         "Field_id"
    "View_fields__0__Field_placement":  "small:0,12; medium:0,6"
    "View_fields__1__Field_id":         "Field_placement"
    "View_fields__1__Field_placement":  "small:0,12; medium:6,6


# A simple example

This example has a label, comment and any number of tags.  It avoids the self-referentiality of the field description example, which helps to make clearer where the various values are coming from.

## Record view description

    { "@id":                "./"
    , "annal:id":           "Tag_view"
    , "annal:type":         "annal:RecordView"
    , "annal:uri":          "annal:view/Tag_view"
    , "annal:record_type":  "annal:DefaultType"
    , "rdfs:label":         "Tagged entity view"
    , "rdfs:comment":       "Tagged entity view, displaying label, command and any number of tags"
    , "annal:view_fields":
      [ { "annal:field_id":             "Example_label"
        , "annal:field_placement":      "small:0,12"
        }
      , { "annal:field_id":             "Example_comment"
        , "annal:field_placement":      "small:0,12"
        }
      , { "annal:repeat_id":            "View_tags"
        , "annal:repeat_label":         "Tags"
        , "annal:repeat_btn_label":     "tag"
        , "annal:repeat_for_values":    "ex:tags"
        , "annal:repeat":
          [ { "annal:field_id":             "Tag_name"
            , "annal:field_placement":      "small:0,12; medium:0,6"
            }
          , { "annal:field_id":             "Tag_label"
            , "annal:field_placement":      "small:0,12; medium:6,6"
            }
          ]
        }
      ]
    }

## Field definitions

### Field: Example_label

    { "@id":                "annal:fields/Example_label"
    , "annal:id":           "Example_label"
    , "annal:type":         "annal:Field"
    , "rdfs:label":         "Label"
    , "rdfs:comment":       "A short label phrase for the tagged entity."
    , "annal:field_name":   "entity_label"
    , "annal:field_render": "annal:field_render/Text"
    , "annal:value_type":   "annal:Text"
    , "annal:placeholder":  "(tag)"
    , "annal:property_uri": "rdfs:label"
    }

### Field: Example_comment

    { "@id":                "annal:fields/Example_comment"
    , "annal:id":           "Example_comment"
    , "annal:type":         "annal:Field"
    , "rdfs:label":         "Label"
    , "rdfs:comment":       "A description of the tagged entity."
    , "annal:field_name":   "entity_comment"
    , "annal:field_render": "annal:field_render/Textarea"
    , "annal:value_type":   "annal:Longtext"
    , "annal:placeholder":  "(tag)"
    , "annal:property_uri": "rdfs:comment"
    }

### Field: Tag_name

    { "@id":                "annal:fields/Tag_name"
    , "annal:id":           "Tag_name"
    , "annal:type":         "annal:Field"
    , "rdfs:label":         "Tag"
    , "rdfs:comment":       "A short identifier name used to tag an entity."
    , "annal:field_name":   "tag_name"
    , "annal:field_render": "annal:field_render/Text"
    , "annal:value_type":   "annal:Slug"
    , "annal:placeholder":  "(tag)"
    , "annal:property_uri": "ex:tagname"
    }

### Field: Tag_label

    { "@id":                "annal:fields/Tag_label"
    , "annal:id":           "Tag_label"
    , "annal:type":         "annal:Field"
    , "rdfs:label":         "Label"
    , "rdfs:comment":       "A short label phrase for a tag."
    , "annal:field_name":   "tag_label"
    , "annal:field_render": "annal:field_render/Text"
    , "annal:value_type":   "annal:Text"
    , "annal:placeholder":  "(tag)"
    , "annal:property_uri": "ex:taglabel"
    }

## Entity

    { "@id":                "ex:Example"
    , "annal:id":           "Example"
    , "annal:type":         "Example_type"
    , "rdfs:label":         "Example label"
    , "rdfs:comment":       "Example comment"
    , "ex:tags":
      [ { "ex:tagname": "tag1", "ex:taglabel": "tag1 label" }
      , { "ex:tagname": "tag2", "ex:taglabel": "tag2 label" }
      ]
    }

## Context

    "title":                <title>
    "coll_id":              <coll_id>
    "type_id":              <type_id>
    "view_id":              <view_id>
    "action":               <action>
    "continuation_uri":     <continuation_uri>

    "entity_uri":           "ex:Example"
    "entity_id":            "Example"
    "entity_type":          "Example_type"
    "orig_id":              "Example"
    "orig_type":            "Example_type"

    "entity_label":         "Example label"
    "entity_comment":       "Example comment"
    "tags":
      [ { "tag_name": "tag1", "tag_label": "tag1 label" }
      , { "tag_name": "tag2", "tag_label": "tag2 label" }
      ]

    "fields":
        0:  FieldValueMap(
              c="fields", 
              f=FieldDescription(
                  { "annal:field_id":        "Example_label"
                  , "annal:field_placement": "small:0,12"
                  })
              )
        1:  FieldValueMap(
              c="fields", 
              f=FieldDescription(
                  { "annal:field_id":        "Example_comment"
                  , "annal:field_placement": "small:0,12"
                  })
              )
        2:  RepeatValuesMap(
              c="tags",
              e="ex:tags",
              f=FieldListValueMap(
                  // type="Tag",
                  // id_field="field_id",
                  fields=(
                      [ FieldDescription(
                          { "annal:field_id":        "Tag_name"
                          , "annal:field_placement": "small:0,12; medium:0,6"
                          })
                      , FieldDescription(
                          { "annal:field_id":        "Tag_label"
                          , "annal:field_placement": "small:0,12; medium:6,6"
                          })
                      ])
                  ),
              r=RepeatDescription(
                  { 'annal:repeat_id':        "View_tags"       // ID for this repeat group
                  , 'annal:repeat_label':     "Tags"            // Label for this repeat group
                  , 'annal:repeat_btn_label': "tag"             // Button label for add/remove buttons
                  })
              )

## Form data

    # Information from hidden fields
    "orig_id":              "Example"
    "orig_type":            "Example_type"
    "view_id":              <view_id>
    "action":               <action>
    "continuation_uri":     <continuation_uri>

    # Generated from field descriptions
    "entity_label":        "Example label"
    "entity_comment":      "Example comment"

    # Generated from repeat field group description
    "View_tags__0__Tag_name":         "tag1"
    "View_tags__0__Tag_label":        "tag1 label"
    "View_tags__1__Tag_name":         "tag2"
    "View_tags__1__Tag_label":        "tag2 label"


# Required to implement

* `FieldDescription` - object describing a field, and methods to perform manipulations.
  (part done in entityeditbase.get_field_context)
  - Done.
* `RepeatDescription` - object describing a repeated values group, and methods to perform manipulations.
  (part done in entityeditbase.get_repeat_context; maybe to be subsumed by RepeatValuesMap?)
  - Done.
* `SimpleValueMap` - a direct mapping between an entity field, a context field and a form field.
  - Already done.
* `FieldValueMap` - an indirect mapping between an entity field, a context field and a form field, controlled by field description data (cf. FieldDescription)  Implemented, but update to use FieldDescription values.
  - Already works with FieldDescription values.
* `FieldListValueMap` - try to replace existing ad-hoc logic (cf. EntityEditBase.get_form_entityvaluemap? various functions?) for dealing with field mapping.  
  Compared with GroupRepeatMap, the entity selection is explicit.
  This could be suitable to replace GroupRepeatMap.
* `RepeatValuesMap` - this describes a group of repeated fields.

The value map objects are constructed to take account of a particular view description, and all support the following methods:

* `map_entity_to_context(context, entity_values, extras={})` - maps entity values, usually augmented by entity-independent "extras" values, adding the resulting values to the supplied `context` dictionary.  The form of expected entity_values may be constrained by the particular value mapping class used.
* `map_form_to_entity(values, form_data)` - maps form data to entity value fields, which are added to or replaced in the supplied `values` dictionary.
* `map_form_to_context(context, form_data, extras={})`



