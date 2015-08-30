# Annalist TODO

NOTE: this document is used for short-term working notes; longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] HOWTOs for common tasks; task-oriented documentation
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.
- [ ] New demo screencasts


# Version 0.1.17, towards 0.1.18

- [x] BUG: if alternative field is defined for "Entity_id" (e.g. for different label), can't save entity.  Probably because of internal expected form field name not used?  When RenderType is "EntityId, force use of standard field name?  Similar for "EntityTypeId"?
    - workaround until fix: always use "Entity_id" for field id in view.
    - fix applied: EntityId and EntityTypeId renderers used fixed field name
- [x] BUG: if Value_entity field does not include "refer to type" value, barfs with 500 error.  (Fixed but needs testing.)
- [x] BUG: Multifield ref inside a repeat field not occupying the entire width of the field generates messed up layout of labels vs content.  (Content is OK, labels not.  Maybe need an additional layer of row/cols for the headers in the multifield ref?)
- [x] BUG: import resource in new entity raises internal error.
- [x] BUG: import image when changing record ID (or on new record?) gives error.
- [x] BUG: import image when changing record ID causes error on save
- [x] BUG: if >1 repeated field group is selected for deletion, only the last is deleted
- [ ] BUG: follow links to edit view, then close out, does not return to entity view.
    - "View description" continuation is OK
    - "View description" > "Edit" continuation is OK
    - after "Move up", continuation is lost
- [x] Update file upload logic to use `responseinfo`, following pattern of import.
- [x] Factor out common code between upload/import logic.
- [x] Built-in `Entity_id` and `Entity_label` fields have non-standard position/size values
- [x] Missing enumerated value reference: provide better diagnostic
- [x] Missing enumerated value field: displays blank; should be diagnostic
- [x] Revise add field buttons to use save+redirect rather than re-render
- [x] Introduce separate data-compatibility version (may lag current version)
- [x] Enum selection - include labels in dropdown (then can use built-in IDs more easily)
- [x] _group annal:record_type fields updated to treat grouped field description data as subtype.
- [x] Update save_entity to return responseinfo
- [x] Confirmation message when resource is imported/uploaded
- [x] Use responseinfo values for status reporting to user
    - changes made for save and import.  Make others as the need arises.
- [x] Option to re-order fields on view form
    - [x] add move-up/move-down buttons
    - [x] add handler logic to reorder list when move up/down clicked
    - [x] test cases - top/middle/bottom, up/down
- [ ] Multiple URIs for type, and instances of type - add "supertypes" field
      to type description, and propagate these to the @types field of created 
      instances.
      - [ ] Create new supertype URIs field in type descrioption
          - [x] Field: Type_supertype_uris
          - [x] Group: Type_supertype_uris
          - [x] Field: Type_supertype_uri
          - [ ] Add field to type view
      - [x] entitytypeinfo.create_entity: return ['@type'] as list
      - [ ] entitytypeinfo.create_entity: copy types from record type description to ['@type']
          - this is the key function, used by create/save/rename entities
      - [ ] test case: create type with supertype; create instance; check @type value of instance
          - [ ] Update tests in rest_recordtype to include supertypes field:
              - updating recordtype_create_values should be enough
          - [ ] gneeric entity editing tests should do the rest 
              - expect failures when new types are added to entities
- [ ] When testing site data, check for entity type of repeated field match with value type of referencing field and group?
- [ ] When using "+" to add an enum entry, also need quick route to edit entry?
    - existing tests generate __new button submission - cf. render_select.py
    - logic in handler to invoke edit if value selected
    - when rendering, use &#x270D; where value is selected
    - default use &#x270D; rather than "+"
    - add javascript to update rendering when value selected/deselected
    - rename __new to __edit?
    - when item is selected, change "+" to edit?  (Use &#x270D; - "writing hand" ?)
    - how to select code based on current value?
        - Template logic?  Code generates context?  `bound_field` attribute?  javascript?

(release 0.1.18?)

- [ ] Usability: 3 key tasks need to be easier (at the level of a single form fill-out):
    - [ ] Create a new type+view+list, suitably interconnected
    - [x] Define a new field type and add to a view
    - [ ] Create repeating fields in a view.  (a) Define a repeating field type and add to view, or (b) define a repeating group containing an existing field type, and add to a view. (a) could a checkbox choice on the previous task.  See also: [#41](https://github.com/gklyne/annalist/issues/41)
    - Currently it gets tedious creating view forms with repeated fields; need to figure a way to streamline this.
    - See also discussion below of introducing "tasks" - this would be an early candidate for that.
    - Need to think how the interface would work.  Option to add "task" button to any form?
- [ ] Simplified field-definition interface (hide confusing detail; use javascript to hide/expose fields based on selection from simple enumeration of field types?)

(release?)

- [ ] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [ ] Think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
    - [ ] JSON-LD @contexts support
    - [ ] Alternative RDF formats support (e.g. content negotiation)

(release?)

- [ ] Re-work site/collection structure to use a cascaded inheritance between collections.  Eliminate site data as separate thing, but instead use a standard, read-only, built-in collection (e.g. "_site_defs"?). This will allow an empty collection to be used as a template for a new collection.  As with site data, edits are always added to the current collection.
- [ ] Initially, single inheritance path for definitions, but consider possibility of multiple (branching) inheritence.  Precedence?
- [ ] The bibiographic definitions currently part of site data should be mived to a "built-in" collection and inherited only when required.

(release?)

- [ ] Add "CodeArea" field type for unflowed, unformatted text with non-propo font
- [ ] Form field layout: introduce padding so the fields lay out as indicated by the position value.  Add field padding so that display position is as expected (if possible)
    - RenderFieldValue.label_view and .label_edit seem to be the key functions.
    - How to carry context forward?
    - Possibly precompute padding?
        - This would require logic in fieldlistvaluemap, fielddescription and render_placement
        - plus new logic to render the padding elements
    - Another option: take field-loop out of template and run it as a `render_all_fields` method
        - still needs placement parser to return position+width information

(release?)

- [ ] Use site/collection data to populate help panes on displays; use Markdown.
- [ ] Login window: implement "Local" as a provider, authenticated against the local Django user base.
- [ ] Login: support continuation URI

- [ ] Easy way to view log; from command line (via annalist-manager); from web site (link somewhere)
    - [x] annalist-manager serverlog command returns log file name
    - [ ] site link to download log, if admin permissions
    - [ ] rotate log files (max 5Mb?) (cf. [RotatingFileHandler](https://docs.python.org/2/library/logging.handlers.html#logging.handlers.RotatingFileHandler))
- [ ] profile_uri now not included in Google JSON file of client secrets
    - use profile_uri="https://www.googleapis.com/plus/v1/people/me/openIdConnect" directly?
    - cf. oauth2/views.py:364
- [ ] annalist-manager options for users, consider:
    - [ ] annalist-manager createlocaluser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager setuserpermissions [ username [ permissions ] ] [ CONFIG ]
- [ ] Add software version to site_meta.
    - [ ] Add when creating site
        - as part of installation
    - [ ] Update when updating site
        - as part of installation
    - [ ] Check this when accessing site.
        - at server startup.
- [ ] Remove all references to `field_target_type` - where needed, use `field_value_type` instead.

(feature freeze for V0.9alpha?)

- [ ] review renderers and revise to take all message strings from messages.py
- [ ] entityedit view handling: view does not return data entry form values, which can require some special-case handling.  Look into handling special cases in one place (e.g. setting up copies of form values used but not returned.  Currently exhibits as special handling needed for use_view response handling.)
- [ ] Eliminate type-specific render types (i.e. 'Type', 'View', 'List', 'Field', etc.), and any other redundant render types
- [ ] Provide content for the links in the page footer
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] Shared deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [ ] Figure out how to preserve defined users when reinstalling the software.
    - I think it is because the Django sqlite database file is replaced.  Arranging for per-configuration database files (per above) might alleviate this.
    - Seems to be working, but needs explicit testing to make sure.
- [ ] Automated test suite for annalist_manager
    - [ ] annalist-manager initialize [ CONFIG ]
    - [ ] annalist-manager createadminuser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager updateadminuser [ username ] [ CONFIG ]
    - [ ] annalist-manager setdefaultpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager setpublicpermissions [ permissions ] [ CONFIG ]
    - [ ] annalist-manager deleteuser [ username ] [ CONFIG ]
    - [ ] annalist-manager createsitedata [ CONFIG ]
    - [ ] annalist-manager updatesitedata [ CONFIG ]
    - etc.
- [ ] Introduce site-local and/or collection-local CSS to facilitate upgrades with local CSS adaptations.
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Review length restriction on entity/type ids: does it serve any purpose?
- [ ] Checkout default form buttons. See:  http://stackoverflow.com/questions/1963245/multiple-submit-buttons-on-html-form-designate-one-button-as-default/1963305#comment51736986_1963305


Technical debt:

- [ ] Refactor entity edit response handling
- [ ] In render_select.py: remove references to {{field.field_value}} and {{field.field_value_link_continuation}} and use locally generated {{field_labelval}}, etc.
    - [ ] The continuation URI will need to be provided separately in the context (via bound_field?) and mentioned separately in the templates.
    - [ ]remove corresponding special case code in bound_field.
- [ ] The field rendering logic is getting a bit tangled, mainly due to support for uploaded files and multiple field references to a linked entity.  Rethinking this to maintain a clearer separation between "edit" and "view" modes (i.e. separate render classes for each) should rationalize this.  The different modes require multiple methods on different modules in different classes;  can the field description have just 2 renderer references (read/edit) and handle the different modes from there?  (It is field description values that are referenced from templates.)
- [ ] The handling of entity_id and entity_type involves some special case testing in bound_field, dues somewhat to the early template-based logic for field rendering.  Withn the introduction of separate render-templates in views.fields.render_select.py, it may be possible to change the context variables used for this case and remove the special login in bound_field.
- [ ] Similar to above for entity_id, except that it uses a separate template in templates.fields.
- [ ] Can annal:field_name in field descriptions be eliminated with revised entity_id and entity_type logic?
- [ ] Check EntityId and EntityTypeId renderers appear only at top-level in entity view


Usability notes:

- [ ] Persist item selection to refreshed display when move-up/movedown clicked?
- [ ] Easy(er) switch to alternative views (e.g. manufacture, performance for Carolan events)
- [ ] OR... allow an entity to specify its own default view?
- [ ] Type/List/View dropdowns: normally show only those types/lists/views defined by the current collection, but ensure it is still reasonably easy to get lists of built-in types as well.  Details need to be worked out.
- [ ] View forms need title (indicating type of thing viewed)?  Or let user define label for Id field?
- [ ] Provide field type that can be used to place fixed annotations/instructions in a form
- [ ] Add title attributes to all buttons - used as tooltip
- [ ] Add title to field controls based on field help, to use as tooltip.
- [ ] Introduce notion of "Task", based on form, but linked to "script" action.
    - [ ] Create a "wizard-like" (or one-form) interface for creating type+list+view set.
        - test by creating contacts/supplies listy for CruisingLog
    - [ ] Create a "wizard-like" (or one-form) interface for creating field+field-group set.
        - needs to create (a) individual fields in group, (b) field group and (c) field referring to group.
    - [ ] Procedure for creating type + view definition + list definition + field definitions from a simple overview description
    - [ ] Procedure for creating enumeration type from simple description of options
    - [ ] Procedure to migrate textual type annotations to enumeration types
    - [ ] Simplify repetitive data entry; e.g.
        - Use-case: create bibliographic author details from just full name entered
        - [ ] derived field (possibly hidden) with a rule to guide its creation from other fields in a view
        - [ ] default value from other field (possibly from a derived field)
        - [ ] initial value/identifier templates (e.g. create ID from current date)
            - NOTE: default and initial values behave differently
        - [ ] "view source" record editing (of JSON), with post-entry syntax checking.
- [ ] Getting type URI/CURIE to match across type/list is too fragile.  Avoid using selector for this unless it's really needed?  In particular, getting the entity type for a field is error-prone.
- [ ] Use pop-up text based on field comment to tell user how a field value is used
- [ ] Option to re-order fields on view form
- [ ] When creating type, default URI to be based on id entered
- [ ] Instead of separate link on the login page, have "Local" as a login service option.
- [ ] List display paging
- [ ] When generating a view of an enumerated value, push logic for finding link into the renderer, so that availability of field link does not depend on whether field is available for the selected view.  (Try changing entity type of field to random value - can no longer browse to field description from view/group description)


Notes for Future TODOs:

(Collecting ideas here: consider expand them in the GitHub issues list.)

- [ ] Allow comment field to be left blank and use label instead?  Maybe not: later, allow comment field to default to label.
- [ ] field renderer for unified import or upload resource?
- [ ] `annal:member` - used to "lift" repeated values to the property that references a repeat group?
- [ ] Improve reporting of errors due to invalid view/field definitions, etc.
- [ ] add 404 handling logic to generate message and return to next continuation up the chain.
    - [ ] reinstate get_entity_data in displayinfo, and include 404 response logic.
    - [ ] update entityedit c.line_116 to use new displayinfo function.  This will mean that all 404 response logic is concentrated in the displayinfo module. (Apart from statichack.)
    - [ ] update displayinfo so that it receives a copy of the continuation data when initialized.
    - [ ] pass continuation data into view_setup, list_setup, collection_view_setup for ^^.  For site, just use default/empty continuation.
    - [ ] Calling sites to collect continuation are: EntityGenericListView.get, EntityGenericListView.post, EntityDeleteConfirmedBaseView.complete_remove_entity, GenericEntityEditView.get, GenericEntityEditView.post.
- [ ] ORCID authentication - apparently OAuth2 based (cf. contact at JISC RDS workshop).  See also http://support.orcid.org/forums/175591-orcid-ideas-forum/suggestions/6478669-provide-authentication-with-openid-connect
- [ ] Image collections - check out http://iiif.io/, http://showcase.iiif.io/, https://github.com/pulibrary/loris
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication?
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s)?  But note that general philosophy is to avoid unnecessary validity checks that might impede data entry.
- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of type definitions.
- [ ] Make default values smarter; e.g. field renderer logic to scan collection data for candidates?
- [ ] Allow type definition to include template for new id, e.g. based on current date
- [ ] Use local prefix for type URI (when prefixes are handled properly); e.g. coll:Type/<id>
- [ ] Associate a prefix with a collection? 
- [ ] Provide a way to edit collection metadata (e.g. link from Customize page)
- [ ] Provide a way to edit site metadata (e.g. via link from site front page)
- [ ] Provide a way to view/edit site user permissions (e.g. via link from site front page)
- [ ] Provide a way to view/edit site type/view/list/etc descriptions (e.g. via link from site front page)
    - not edit: site data should be stable and controlled.  Consider collection structure inheritiance instead.
- [ ] Undefined list error display, or any error - include link to collection in top bar
- [ ] Help display for view: use commentary text from view descrtiption; thus can tailor help for each view.
- [ ] Use markdown directly for help text
- [ ] Think about fields that return subgraph
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
    - cf. [JSON-LD framing](http://json-ld.org/spec/latest/json-ld-framing/)
- [ ] For rendering of additional info, think about template-based URIs filled in from other data.  (e.g. URI to pull an image from CLAROS, or Google graph API like)
- [ ] Generate form-level DIFF displays from git JSON diffs
- [ ] 3D rendering - check out JSMOL - http://wiki.jmol.org/index.php/JSmol
- [ ] Visualize data structures from view definitions; generate OWL descriptions; etc.
- [ ] Remixing spreadsheets: spreadsheet generation from queries as well as ingesting through data bridges.
- [ ] SPARQL data bridge: use copmbination opf SPARQL CONSTRUCT query + JSON-LD frame?
- [ ] View selection based on pattern match; e.g. JSON PATCH "Test" operation.
- [ ] git/github integration
    - [ ] annalist-manager options to load/save collection using git (assuming git is installed)
    - [ ] internal options to save history in per-collection git repo


# Feedback

* https://github.com/gklyne/annalist/issues/40


----
