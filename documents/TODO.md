# Annalist TODO

NOTE: this document is used for short-term working notes; some longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] Update tutorial
    - Also cover inheritance of definitions?
- [ ] New demo screencast(s)
- [ ] HOWTOs for common tasks; task-oriented documentation
    - Have tutorial; can this be used?
- [ ] Add documentation for view Type, View, List and Group forms (similar to view Field ...)
- [x] Initial corpus of FAQs
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.

See also: https://www.divio.com/en/blog/documentation/


# Version 0.5.7, towards 0.5.8

- [x] BUG: delete list view while viewing that list results in obscure error message.
    - Improve error handling to use alternative list/view definition
- [x] BUG: Turtle generation from "Smoke" collection journal entry causes internal errors
    - Error reading bad context file, caused by Annalist data errors, which have been fixed.
    - Need to look into improving context-generation diagnostics.
    - Also caused by trailing spoace on URL: need to check valid URLs; can catch errors?
    - Added logic to flag error and add details to output.
- [x] Fix some test cases that were failing due to message text changes.
    - NOTE: `test_entitydefaultlist` and `test_entitygenericlist` now have logic to test messages using definitions in `message`.  In the longer term, all test cases should do this so they don't fail if the language is changed.
- [x] Review message text; update more tests to expect text as defined in messages module.
- [x] Introduce superproperty/ies field and button to create subproperty field definition
    - [x] Collection methods to access field definitions (model on types)
    - [x] Cache classes for fields (model on types)
    - [x] RecordField hook to update collection cache
    - [x] Test cases for new classes and methods
    - [x] Update collection to use field cache
    - [x] Update cache flush logic where used
    - [x] Test suite provide default property URIs 
    - [x] RecordField accesses should use collecton cache
    - [x] Cacheing site values separately: no need to flush as they don't change
    - [x] Field definition to include superproperty URI list
    - [x] When selecting data element to display in a field, look for subproperties as well as the specified field property.
        - [x] Add subproperty discovery logic to bound_field
        - [x] Update fieldvaluemap.map_form_to_entity so it looks for subproperty to update.
        - [x] Update field mappers to make 'map_form_to_entity_repeated_item' implementations more consistent.
        - It appears that the logic for this should be in 'bound_field'
        - All other code seems to be concerned with creating a bound field object.
        - The collection (and hence field cache) is available via the bound FieldDescription.
        - What about saving field value?: need to remember property URI used?
            - fieldvaluemap.map_form_to_entity passes property URI to value mapper decode_store method
            - fieldvaluemap.map_entity_to_context just passes the field description to bound_field constructor.  (Level imbalance here?)
    - [x] Review abstractions and interactions around:
        - [x] bound_field, add:
            - [x] 'render' (ref field_renderer)
            - [x] 'value_mapper'
        - [x] New field_renderer object accessed by bound_field for field rendering
        - [x] Rework field rendering logic to use new structure
        - [x] Remove rendering methods from field description
        - [x] bound_field access to FieldDecription: use methods not dictionary
        - [x] Eliminate render mode logic in render_fieldvalue
    - [x] Add test cases for subproperty access
    - [x] Add test cases for subproperty list field access/update (with subproperty values)
    - [x] Add "define subproperty" task button to field definition.
    - [x] Add test case for "define subproperty" task button
- [x] Add property hierarchy to CIDOC CRM definitions
- [x] Create FAQ for defining subproperties

(Sub-release?)

- [ ] Bound_field access to FieldDecription: use methods not dictionary
    - [ ] Update test case context checking (see bound_field holding comments)
- [x] Render modes:  instead of a separate function for each mode, pass parameter to each renderer and select at the point of rendering (e.g. see render_fieldvalue.render_mode)
    - this should avoid the need for the multiple layers of wrapping and duplication of render mode functions.  Field description should carry just a single renderer; figure later what to do with it.)
- [ ] In render_select.py: remove references to {{field.field_value}} and {{field.field_value_link_continuation}} and use locally generated {{field_labelval}}, etc.
    - [ ] The continuation URI will need to be provided separately in the context (via bound_field?) and mentioned separately in the templates.
    - [ ] Remove corresponding special case code in bound_field.
- [ ] The handling of entity_id and entity_type involves some special case testing in bound_field, due somewhat to the early template-based logic for field rendering.  With the introduction of separate render-templates in views.fields.render_select.py, it may be possible to change the context variables used for this case and remove the special logic in bound_field.
- [ ] Similar to above for entity_id, except that it uses a separate template in templates.fields.
- [ ] Can annal:field_name in field descriptions be eliminated with revised entity_id and entity_type logic?
- [ ] Update pip to latest version in python environment (for continued testing)
- [ ] Update Django version used to latest version designated for long term support (1.8? 2.x?)
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] deploy `letsencrypt` certs on all `annalist.net` servers and force use of HTTPS.
        - [ ] Document setup process.
    - [ ] Check out https://docs.djangoproject.com/en/1.8/ref/django-admin/#django-admin-check
    - [ ] Shared/personal deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?

(Sub-release?)

- [ ] Consider new render type for URI reference (or fragment) relative to URI specified in another entity.
    - Use-case for this is Climb! data where MEI resource should be referenced just once, with MEI embodiments listing just the fragment identifiers.
- [ ] Make it easier to create subtype + view + list...
    - Get some experience with initial solution; (previous release)
    - Test cases for subtype creation stages
- [ ] With implementation of subproperties, are per-type field aliases still needed?
    - Possible per-type subproperties?
    - Maybe use these for property updates rather than looking for existing property usage?
    - Is this an issue?  Need some experience here.
- [ ] How to deal with reference to entity that has a permanent URI defined (per annal:uri)?
    - Currently, reference is internal relative reference, but for exported linked data the permanent URI should be used (e.g. references to concept tags or types).
    - If absolute URI is stored, can local reference be discovered for hyperlinking?
    - I think evolvability is served by making these exchangeable
- [ ] provide for site and collection home page content negotiation, so applications can find data by following links.  As a minimum, include (and document) URL templates in response headers for accessing data.  See `FAQs/FAQ_URL_structure.md`.
- [ ] Eliminate type-specific render types (i.e. 'Type', 'View', 'List', 'Field', etc.), and any other redundant render types.  Also "RepeatGroup" and "RepeatGroupRow".
- [ ] Remove surplus fields from context when context generation/migration issues are settled
    - cf. collection.set_field_uri_jsonld_context, collection.get_coll_jsonld_context (fid, vid, gid, etc.)
- [ ] *delete views: rationalize into single view?
- [.] performance tuning
    - [x] in EntityTypeInfo: cache type hierarchy for each collection/request; clear when setting up
    - [x] look into entity cacheing (esp. RecordType) for performance improvement
        - partly done per-collection - is this enough?
    - [ ] Re-think access to entities and types:
        - [x] There is repeated reading of RecordType values in EntityFinder
              (cf. collection.types() and EntityTypeInfo constructor; also URI access)
        - [x] Need more direct way to locate type (and other entities?) by URI
        - [ ] Review common mechanism to retrieve URI for entity?  
              (Current mechanism fixes use of annal:uri for all entities; maybe OK)
        - [x] Think about how to optimize retrieval of subtypes/supertypes
        - [x] Do special case for types, or more generic caching approach?
- [ ] review renderers and revise to take all message strings from messages.py
- [ ] review title/heading strings and revise to take all message strings from messages.py
- [ ] entityedit view handling: view does not return data entry form values, which can require some special-case handling.  Look into handling special cases in one place (e.g. setting up copies of form values used but not returned.  Currently exhibits as special handling needed for use_view response handling.)
- [ ] entityedit view handling: refactor save entity logic to follow a pattern of extract, validate, update in separate functions so that these can be recombined in different ways.  Note effect on `save_invoke_task` method, and elsewhere.
- [ ] Review nomenclature, especially labels, for all site data
- [ ] Provide content for the links in the page footer
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
- [ ] Review docker files: reduce number of separate commands used; always build on clean python setup
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Checkout default form buttons. See:  http://stackoverflow.com/questions/1963245/multiple-submit-buttons-on-html-form-designate-one-button-as-default/1963305#comment51736986_1963305
- [ ] Move outstanding TODOs to GitHub issues

Technical debt:

- [ ] For models and views, define a module that exports classes and functions directly so that importers don't have to name the individual modules in import statements. (Search for instances of "import annalist.models." and import "annalist.views.")
- [ ] Implement in-memory entity storage to speed up test suite, and lay groundwork for LDP back-end
- [ ] Move top menu selection/formatting logic from template into code (e.g. context returned by DisplayInfo?)
- [ ] Built-in type id's: use definitions from `models.entitytypeinfo` rather than literal strings
    - [ ] update 'models'
    - [ ] update 'views'
    - [ ] update 'tests'
    - [ ] update 'annalist-manager'
- [ ] Consider `views.site`, `views.collection` refactor to use `views.displayinfo`
- [ ] Implement "get the data" link as a field renderer?
- [ ] review view URL returned for entities found with alternative parentage:
    - currently force URL returned to be that of original parent, not alt. 
    - This is done to minimize disruption to tests while changing logic.
    - See: _entityviewurl member variable
    - logic is handled in `Entity.try_alt_parentage` and _init_child`
    - may want to consider promoting entityviewurl to constructor parameter for all Entity.
- [ ] Delay accessing settings data until actually needed, so that new dependencies (e.g. models on views) don't cause premature selection.  This will help to avoid certain unexpected problems cropping up as happened with release 0.1.22 logging setup for annalist-manager.
- [ ] After reworking site data access, review `layout.py` and patterns for accessing entities, metadata, context data, etc.
    - The various relative references for accessing context data are particularly unclear in the current software.
- [ ] Inconsistent `@id` values in site data ("." or "<type-id>/<entity-id>")
- [ ] "Customize" view style getting out of sync with other page styles
    - possible enhancements to form generator to generate customize page using form logic?
- [ ] Refactor entity edit response handling
- [ ] Review handling of composite type+entity identifiers in list display selections to bring in line with mechanisms used for drop-down choicess.
- [ ] Review field mapping modules in views/form_utils to be more readable and consistent
    - Start with 'fieldvaluemap', look for comments in code
    - Notes:
        - EntityValueMap 
            - Handles entity->context and form->entity mapping for a complete entity view.
            - methods:
                - add_map_entry
                - map_value_to_context
                - map_form_data_to_values
            - invoked by entitiedit via get_view_entityvaluemap
            - invoked by entitylist via get_list_entityvaluemap
                - (has some ad-hoc logic to construct a list definition)
        - FieldValueMap, FieldListValueMap, FieldRowValueMap, RepeatValuesMap, SimpleValueMap 
            - Handles entity->context and form->entity mapping for parts of an entity view
            - methods: 
                - map_entity_to_context
                - map_form_to_entity
                - map_form_to_entity_repeated_item
                - get_structure_description (for diagnostics only?)
            - module 'fieldlistvaluemap' also has logic for organizing fields in rows
- [ ] Tidy up FieldDescription and usage
    - Notes:
        - FieldDefinition - definition of field, bound to collection
            - also accessible as a dictionary (rather breaks abstraction)
            - currently has logic spread unevenly over bound_field and FieldDefinition
        - Dependency graph, avoiding loops:
            -- FieldDescription
            -> FieldRenderer
            -> find_renderers
            -> render_repeatgroup.RenderRepeatGroup
            -> render_fieldvalue, bound_field
            - NOTE: bound_field uses FieldDescription values, but does not invoke their construction.
- [ ] The field rendering logic is getting a bit tangled, mainly due to support for uploaded files and multiple field references to a linked entity.  Rethinking this to maintain a clearer separation between "edit" and "view" modes (i.e. separate render classes for each) should rationalize this.  The different modes require multiple methods on different modules in different classes;  can the field description have just 2 renderer references (read/edit) and handle the different modes from there?  (It is field description values that are referenced from templates.)
- [ ] Check EntityId and EntityTypeId renderers appear only at top-level in entity view
- [ ] Installable collection metadata: read from collection directory (currently supplied from table in "annalist.collections")
- [ ] Turtle serialization error: currently returns diagnostic in data returned; would be better to (also) signal problem via HTTP return code.
- [ ] Test cases: use <namespace>.CURIE.??? values rather than literal CURIEs

Data collection definitions:

- [ ] VoID
- [ ] DCAT
- [ ] PROV
- [x] CRM


Usability notes:

- [ ] Provide renderer that shows calculated supertype transitive closure?
- [ ] Allow multiple entity deletes from list display 
    - views.entitylist > post - allow and handle multiple ids for delete operation
    - views.displayinfo > confirm_delete_entity_response - handle multiple values, including in message
    - message.REMOVE_ENTITY_DATA - also provide message for multiple entities
    - views.entitydelete - pass list rather than single entityid; use different form value name
    - views.entitydeletebase - update to handle list of entity ids, including for confirmation message.  May need to separate failures from successes?
- [ ] Would be nice to have an easy way to move an edited inherited definition back to the parent collection
    - copied-from field in entity?
- [ ] In field definition, "Entity type" should be drop-dwon, with subtype logic handling an initial dereference to obtain the type URI.
- [ ] Select+"edit" from list display uses list-defined view, not entity type view as when hyperlink is clicked
- [ ] Simplified field-definition interface? (hide confusing detail; use javascript to hide/expose fields based on selection from simple enumeration of field types?)
- [ ] Persist item selection to refreshed display when move-up/movedown clicked?
- [ ] Deprecate "Refer to field" field in field view, and "Field reference" value mode. 
- [ ] Add menu bar link to display content of collection rather than default
    - List of types, linked to lists?
- [ ] When creating type, default URI to be based on id entered (e.g. coll:<type-id>?)
- [ ] List display paging
- [ ] Task button option to copy type+view+list and update names and URIs
    - problems:
        - how is the new type name defined?  (Also the new view and list.)
        - should edits to the current type be saved first?
    - implementation deferred until save entity logic in `entityedit.py` has been refactored: follow a pattern of extract, validate, update in separate functions so that these can be recombined in different ways.
- [ ] When generating a view of an enumerated value, push logic for finding link into the renderer, so that availability of field link does not depend on whether field is available for the selected view.  (Try changing entity type of field to random value - can no longer browse to field description from view/group description)
- [ ] If logout results in loss of authorization to view resource, go to collection view?
    - This could be tricky, as each view does its own auth checks.
    - Would need much better structuring of view dispatching to enable pre-flight auth check.
    - As an edge case, don't worry about this immediately.
- [ ] Try to make changing entity type and entity id follow-through more smoothly.
    - especially when creating a supertype and selecting an appropriate subtype.
- [ ] Better support for type renaming: hunt out all references and rename them too?
- [ ] Consistency checks for references to missing types (e.g. following rename)
- [ ] Introduce notion of "Task", based on form, but linked to "script" action.
    - [x] Create a "wizard-like" (or one-form) interface for creating type+list+view set.
        - test by creating contacts/supplies list for CruisingLog
    - [x] Create a "wizard-like" (or one-form) interface for creating field+field-group set.
        - needs to create (a) individual fields in group, (b) field group and (c) field referring to group.
    - [ ] Create a "wizard-like" (or one-form) interface for creating subtype+view+list from existing type
    - [ ] Procedure for creating type + view definition + list definition + field definitions from a simple overview description
    - [ ] Procedure for creating enumeration type from simple description of options
    - [ ] Procedure to migrate textual type annotations to enumeration types
    - [ ] Renderer for generating back-links to records that reference the current record
    - [ ] Simplify repetitive data entry; e.g.
        - Use-case: create bibliographic author details from just full name entered
        - [ ] derived field (possibly hidden) with a rule to guide its creation from other fields in a view
        - [ ] default value from other field (possibly from a derived field)
        - [ ] initial value/identifier templates (e.g. create ID from current date)
            - NOTE: default and initial values behave differently
        - [ ] "view source" record editing (of JSON), with post-entry syntax checking.
- [ ] Getting type URI/CURIE to match across type/list is too fragile.  Avoid using selector for this unless it's really needed?  In particular, getting the entity type for a field is error-prone.


Notes for Future TODOs:

(Collecting ideas here: consider expand them in the GitHub issues list.)

- [ ] RDF Schema generation for a collection, to include RDFS subtype/subproperty statements and such OWL constraints as can be inferred from the type/view/field definitions.
- [ ] Allow repeating fields to appear in columns (i.e. don't override supplied placement)?
    - Requires rework of logic in views.form_utils.fieldlistvaluemap, in particular to handle nested row structures.  Currently, the field is assumed to be part of a single row.
- [ ] Consider "scope parent" option?  (i.e. current collection and immediate parent, but no more)
- [ ] Final elimination of RecordGroup (field group) entities
    - [ ] Remove class RecordGroup
    - [ ] eliminate _field/Field_groupref instances
    - [ ] eliminate _view/Field_group_view, _list/Field_group_list
    - [ ] eliminate all Group_* fields
    - [ ] Remove field group type URI from annal: namespace
    - [ ] eliminate _type/_group
    - [ ] Remove '_group' from EntityTypeInfo dispatching tables
    - [ ] Clean up dead code:
        - [ ] test_recordfield.py
- [ ] Add facility for import from RDF or SPARQL endpoint.
    - for each defined type, locate all records of that type (which are not also instances of a defined subtype), and use a SPARQL query to extract statements and format the results as JSON-LD.
- [ ] Review how URIs are generated for referenced entities: currently a relative reference is used, which resolves to a local URL for the entity concerned.  But if the entity has a global identifier (`annal:URI`) that should appear in exported data.  One fix is to just use global URIs in text fields when global URIs are expected (e.g. supertypes in class description).  E.g., consider generating:
    "rdfs:subClassOf": [
      { "@id": "Class/Resource", "owl:sameAs": "rdfs:Resource"}
      ]
    - annal:display_type values (List/Grid) are another example to consider.
- [ ] Field option to display item(s) in list (e.g. domain).
    - Generalize to path in list objects?
    - cf. https://tools.ietf.org/html/rfc6901 (JSON pointer)
- [ ] Keyboard shortcuts on forms - C-S to save, ...?
- [ ] Implement at least one other identify provider (ORCID?)
    - [ ] ORCID authentication - apparently OAuth2 based (cf. contact at JISC RDS workshop).
        - See also http://support.orcid.org/forums/175591-orcid-ideas-forum/suggestions/6478669-provide-authentication-with-openid-connect
        - UPDATE: See: 
        -   http://support.orcid.org/knowledgebase/articles/343182
        -   http://support.orcid.org/knowledgebase articles/343182-register-a-public-api-client-application
        -   http://members.orcid.org/api/introduction-orcid-public-api
    - [ ] Other OpenID Connect providers; e.g. see http://openid.net/certification/
        - hard to find actual provider service other than Google
    - [ ] https://aarc-project.eu
    - tried investigating EUDat, which looks promising but fails with invalid certificate
    - see also notes from discussion with Matthew Dovey at CrossRef event in Oxford (EOSC?)
- [ ] Think about facility to make it easier to create identity provider details.  (?)
- [ ] Views providing different perspectives on data; e.g. artifact centres, event centred, etc.  Would need a way to find inbound references as well as outbound.
- [ ] Generate default value type for field based on render type + value mode (to help with consistency)
    - See notes.
- [ ] It would be nice if link field tooltips describe what they link to.
- [ ] Rethink collection overview that allows users to see what is present
    - original thoughts, but review in light of default-view approach adopted:
        - initially, just provide a "What's here" list that displays default list label for all types + link to display list.
        - think about an item list renderer (what is variable?)
        - longer term, this might be a high-level graphical display (like PROV diag.)
        - use this to think about linking to alternative displays
- [ ] Extend/alternative view-text field to combine data from multiple fields (per template)
- [x] From view of list definition, link to show list itself
    - Added "Show this list" task button
- [ ] Embedded code expansion in help text, and maybe other Markdown:
    - [x] {{site}} base URL for site
    - [x] {{coll}} base url for collection
    - [x] {{url:typeid/entityid}} UREL for referenced entity.
    - [ ] {{ref:typeid/entityid}} link for referenced entity, using label from target.
    - [ ] {{field:typeid/entityid#property_uri}} field from referenced entity
- [ ] Think about how to incorporate resources from other collections by reference: feed into data bridges?
- [ ] Think about extending field descriptions to include:
    - [ ] superproperty URIs (similar to supertype URIs in types)
    - [ ] rules that allow inferences of multiple RDF statements; e.g.
        ?a isRecordingOf ?b
        => 
        [ a frbroo:F29_Recording_Event ]
            frbroo:R20F_recorded ?b ;
            frbroo:R21F_created ?a .
    - the above pair might be combined.  We would then want to run the inferences when exporting JSON-LD
- [ ] Introduce site-local and/or collection-local CSS to facilitate upgrades with local CSS adaptations.
- [ ] Issues raised by Cerys in email of 23-Oct-2015.  Some good points there - should break out into issues.
- [ ] consider render type option for repeat group rows without headings? (simple repeat group doesn't hack it).
    - Should be easy to add.  Just need a name.
- [ ] Scrolling through views from list - e.g. Next/Prev item buttons? (Iris G)
- [ ] Option to scan for broken entity references (e.g., due to removal, renaming)
- [ ] Extend task definitions to include validation: allow error reporting
- [ ] Improve reporting of errors due to invalid view/field definitions, etc.
- [ ] add 404 handling logic to generate message and return to next continuation up the chain.
    - [ ] reinstate get_entity_data in displayinfo, and include 404 response logic.
    - [ ] update entityedit c.line_116 to use new displayinfo function.  This will mean that all 404 response logic is concentrated in the displayinfo module. (Apart from statichack.)
    - [ ] update displayinfo so that it receives a copy of the continuation data when initialized.
    - [ ] pass continuation data into view_setup, list_setup, collection_view_setup for ^^.  For site, just use default/empty continuation.
    - [ ] Calling sites to collect continuation are: EntityGenericListView.get, EntityGenericListView.post, EntityDeleteConfirmedBaseView.complete_remove_entity, GenericEntityEditView.get, GenericEntityEditView.post.
- [ ] Image collections - check out http://iiif.io/, http://showcase.iiif.io/, https://github.com/pulibrary/loris
- [ ] Review field placement and layout grid density (16col instead of 12col?)
- [ ] Rationalize common fields to reduce duplication?
    - but note that fields may use different comment/help text, so maybe not.
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s)?  But note that general philosophy is to avoid unnecessary validity checks that might impede data entry.
- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of type definitions.
- [ ] Make default values smarter; e.g. field renderer logic to scan collection data for candidates?
- [ ] Allow type definition to include template for new id, e.g. based on current date
- [ ] Use local prefix for type URI (when prefixes are handled properly); e.g. coll:Type/<id>
- [ ] Associate a prefix with a collection
- [ ] Undefined list error display, or any error - include link to collection in top bar
- [ ] Think about fields that return subgraph
    - how to splice subgraph into parent - "lambda nodes"?
    - does field API support this? Check.
    - cf. [JSON-LD framing](http://json-ld.org/spec/latest/json-ld-framing/)
- [ ] For rendering of additional info, think about template-based URIs filled in from other data.  (e.g. URI to pull an image from CLAROS, or Google graph API like)
- [ ] Generate form-level DIFF displays from git JSON diffs
- [ ] 3D rendering - check out JSMOL - http://wiki.jmol.org/index.php/JSmol
- [ ] Visualize data structures from view definitions; generate OWL descriptions; etc.
- [ ] Remixing spreadsheets: spreadsheet generation from queries as well as ingesting through data bridges.
- [ ] SPARQL data bridge: use combination of SPARQL CONSTRUCT query + JSON-LD frame?
- [ ] View selection based on pattern match; e.g. JSON PATCH "Test" operation.
- [ ] git/github integration
    - [ ] annalist-manager options to load/save collection using git (assuming git is installed)
    - [ ] internal options to save history in per-collection git repo
- [ ] Review small inconsistency: editing collection metadata does not update the collection software version compatibility for that collection.  (Editing any other collection entity does.)  The following comment is from the notes for v0.5.1:
    - Deal with special case of editing collection metadata.  This would need a new set of logic (possibly in entitytypeinfo.py) to distinguish between a containing collection and ancestor for any entity (in almost all cases these would be the same), for a benefit that seems of very small practical value. So, for the time being, this is not being fixed.



# Feedback

* https://github.com/gklyne/annalist/issues/40


----
