# Annalist TODO

NOTE: this document is used for short-term working notes; some longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] Update tutorial
    - Also cover inheritance of definitions?
- [ ] New demo screencast(s)
- [ ] HOWTOs for common tasks; task-oriented documentation
    - Have tutorial; can this be used?
- [ ] Add documentation for view Type, View and List forms (similar to view Field ...)
- [x] Initial corpus of FAQs
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.
    - Add etag / if-match support ?  (does this help with POST? How?)

See also: https://www.divio.com/en/blog/documentation/

# Feedback

* https://github.com/gklyne/annalist/issues/40

# Version 0.5.15, towards 0.5.16

- [x] BUG: Retrieving turtle data in production server fails.  Works OK in dev server.
    - Caused by deadlock on gunicorn single-worker-thread as Turtle output needs to access context via HTTP.
    - Implications for cache management
        - See: documents/notes/20190327-threading-caching-notes.md
- [x] Redesign entity cache to use single cache API thread-safe mechanisms
- [x] Redesign closure cache to use single cache API thread-safe mechanisms
- [x] Generate warning if namespace URI doesn't end with "/" or "#"
    - (kind-of half-hearted check for now as part of JSON-LD context generation)
- [x] Define arbitrary entity ref renderer in core data (renders label as link) 
    - use entity_id renderer with rdfs:label pro
- [x] Under gunicorn, session data seems to get corrupted and logins seem to expire unexpectedlty.
    - I think the problem here is that the gunicorn process is peridoically restarted, resulting in regeneration of the secret key used for keyng session data, CSRF and more.
    - When running Annalist under gunicorn, add ANNALIST_KEY environment variable to prime SECRET_KEY.
- [x] BUG: Apache sample configurations as provided work with Apache 2.2.
    - Updated to work with Apache 2.4, with older directives left as comments.
    
- [x] Added hook for processing entity data before saving
- [x] If property URI in field definition is missing or blank, use field id
- [x] Update reserved identifiers screened by `util.valid_id`
- [x] Review handling of reserved identifiers; don't screen when loading entity.
- [x] Provide language-tagged string renderer? { @value: ..., @language: ... }
- [x] Implement GitHub as authentication IDP option (was originally planning to use ORCiD, but the application registration process was too unwieldy, and it looks as if they require payment.)
- [x] Provide initial content for the links in the page footer.
    - This information can be edited locally.
    - Copies of the initial data are kept separately.

- [ ] From "List entities with type information", click on entry views using form for type, but checkbox + "edit" presents default entity view.
    - This appears to be because the links are generated from te entity data, hence hace access to the actual entity type.  But the edit button works from form data, and only has list type information?
    - Investigate?

(Sub-release?)

- [ ] Documentation and tutorial updates
- [ ] Demo screencast update

- [ ] Install tools and update documentation to use `twine` for package upload.
    - See: https://pypi.org/project/twine/

(Sub-release?)

- [ ] provide for site and collection home page content negotiation, so applications can find data by following links.  As a minimum, include (and document) URL templates in response headers for accessing data.  See `FAQs/FAQ_URL_structure.md`.
- [ ] Eliminate type-specific render types (i.e. 'Type', 'View', 'List', 'Field', etc.), and any other redundant render types.  Also "RepeatGroup" and "RepeatGroupRow".
- [ ] Remove surplus fields from context when context generation/migration issues are settled
    - cf. collection.set_field_uri_jsonld_context, collection.get_coll_jsonld_context (fid, vid, gid, etc.)
- [ ] delete views: rationalize into single view?
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
- [ ] entityedit view handling: provide way for postprocessing hook to provide completion message/warning.  (How do tasks do this?)  Initial use is vocabulary namespace URI checking (currently handled in context generation).
- [ ] entityedit view handling: refactor save entity logic to follow a pattern of extract, validate, update in separate functions so that these can be recombined in different ways.  Note effect on `save_invoke_task` method, and elsewhere.
- [ ] Review nomenclature, especially labels, for all site data (e.g. record/entity)
- [x] Automated test suite for annalist_manager
- [ ] Review docker files: reduce number of separate commands used; always build on clean python setup
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [.] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
    - Started moving toward parameterized context data generation for comparison.
- [ ] Checkout default form buttons. See:  http://stackoverflow.com/questions/1963245/multiple-submit-buttons-on-html-form-designate-one-button-as-default/1963305#comment51736986_1963305
- [ ] Move outstanding TODOs to GitHub issues

(Alpha release 0.9.0??)


Technical debt:


- [ ] See annalist/views/statichack.py ** note TODOs
- [ ] Rename while editing sometimes generates error when saving or invoking new functions that force a save.
    - Consider keeping a list of renames since startup, and applying these when accessing entities to display if the origial access fails.  This may be a better general strategy than rewriting continuation URLs.
- [ ] Check out possible Django compatibility problems:
    - see https://docs.djangoproject.com/en/1.8/ref/django-admin/#django-admin-check
- [ ] Configure for multi-process worker operation
    - [ ] check for code that uses local server state
        - models/collection.py (caches)
        - models/entity.py (id allocation)
        - these are basically caches
    - [ ] need to rethink caching with multiple processes.  Or cache invalidation.
        - store id counter and cache invalidate flag in session and/or Django data?
        - the proper answer is probably to disable in-server caching
        - but how to save transitive closure calculations?  save them in shadow entities?
        - See https://stackoverflow.com/a/868731/324122 (Memcached with Python)
- [x] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [x] Shared/personal deployment should generate a new secret key in settings
    - [x] Need way to cleanly shut down server processes (annalist-manager option?)
    - [x] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [ ] When accessing fields via subproperties of the field definition key, only the first subproperty found is used.  This means that, for repeated fields using different subproperties, only values for one of those subproperties are returned.  Can method `get_field_value_key` be eliminated so that the value access logic canm probe multiple values as appropriate.  Or return a list and handle accoordingly.  This still leaves questions of what to do when updating a value.
    - see FieldDescription.get_field_value_key and bound_field.get_field_value_key
    - There are relatively few references to `get_field_value_key`, but the value is stored in some field mappers.
- [ ] Apply id update in migration logic for all entity types?  (cf. collection)
- [ ] For models and views, define a module that exports classes and functions directly so that importers don't have to name the individual modules in import statements. (Search for instances of "import annalist.models." and import "annalist.views.")
- [ ] Move top menu selection/formatting logic from template into code (e.g. context returned by DisplayInfo?)
- [ ] Built-in type id's: use definitions from `models.entitytypeinfo` rather than literal strings
    - [ ] update 'models'
    - [ ] update 'views'
    - [ ] update 'tests'
    - [ ] update 'annalist-manager'
- [ ] Consider `views.site`, `views.collection` refactor to use `views.displayinfo`
- [ ] Implement "get the data" link as a field renderer?
- [ ] review view URL returned for entities found with alternative parentage:
    - currently forces URL returned to be that of original parent, not alt. 
    - This is done to minimize disruption to tests while changing logic.
    - See: _entityviewurl member variable
    - logic is handled in `Entity.try_alt_parentage` and `_init_child`
    - may want to consider promoting entityviewurl to constructor parameter for all Entity types.
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
- [ ] Test cases: use <namespace>.CURIE.:: values rather than literal CURIEs
    -
- [ ] Change entity type causing 500 error? How?  (Only with invalid data.)


Data collection definitions:

- [ ] VoID
- [ ] DCAT
- [ ] PROV
- [x] OA
- [x] CRM


Usability notes:

- [ ] After copy entity, and edit new entity values, returns to view of original entity: would be better to return to view of copy if all is well.
- [ ] Review method of calculating label widths for fields: consider table lookup that can work with widths that are not sub-multiple of 12 (e.g. 9?).  Problem is that actual width needs to be presented as 12ths of smaller field - how to maintain reasonable alignments?
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
    - Can error message be improved to clarify what is happening?
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

- [ ] Try to provide more seamless interaction between permanent URIs (annal:URI) and local URLs. To what extent can an `annal:uri` property value be used in place of a local reference?
    - The main requirement to date is to be able to export data with permanent URIs, for compatibility with other systems (e.g., EMPlaces data).
    - If exported data is intended to include directly dereferencable links (back to their Annalist source), then the permanent URI isn't the right option.  How to distinguish these cases?
    - When processing data locally, it may be possible to recognize/reference entities bvy their permanent URI as well as their local reference.  This would probably require some kind of lookaside table.
    - For the time being, we are relying on conversion software to export/import data in the required formats.  Maybe we need more experience of this?
    - An interim step could be to (optionally?) use `annal:uri` values, where available, in place of local references when exporting Turtle data.
- [ ] Update Django version used to latest version designated for long term support
    - This will mean cutting adrift from Python 2 support.
    - Leaving this until after version 1 is released.
- [ ] Record timestamp in data records (created,updated)
    - Generate etag too
- [ ] New field renderer for displaying/selecting/entering type URIs, using scan of types
- [ ] Implement in-memory entity storage to speed up test suite, and lay groundwork for LDP back-end definitions.
- [ ] Consider new render type for URI reference (or fragment) relative to URI specified in another entity.
    - Use-case for this is Climb! data where MEI resource should be referenced just once, with MEI embodiments listing just the fragment identifiers.
- [ ] Make it easier to create subtype + view + list...
    - Get some experience with initial solution; (previous release)
    - Test cases for subtype creation stages
- [ ] With implementation of subproperties, are per-type field aliases still needed?
    - Possible per-type subproperties?
    - Maybe use these for property updates rather than looking for existing property usage?
    - Is this an issue?  Need some experience here.
    - NOTE: system attempts to preserve subproperties used; aiases are migrated.

- [ ] How to deal with reference to entity that has a permanent URI defined (per annal:uri)?
    - Currently, reference is internal relative reference, but for exported linked data the permanent URI should be used (e.g. references to concept tags or types).
    - If absolute URI is stored, can local reference be discovered for hyperlinking?
    - I think evolvability is served by making these exchangeable
- [ ] Review how URIs are generated for referenced entities: currently a relative reference is used, which resolves to a local URL for the entity concerned.  But if the entity has a global identifier (`annal:uri`) that should appear in exported data.  One fix is to just use global URIs in text fields when global URIs are expected (e.g. supertypes in class description).  E.g., consider generating:
    "rdfs:subClassOf": [
      { "@id": "Class/Resource", "owl:sameAs": "rdfs:Resource"}
      ]
    - annal:display_type values (List/Grid) are another example to consider.

- [ ] RDF Schema generation for a collection, to include RDFS subtype/subproperty statements and such OWL constraints as can be inferred from the type/view/field definitions.
- [ ] Allow repeating fields to appear in columns (i.e. don't override supplied placement)?
    - Requires rework of logic in views.form_utils.fieldlistvaluemap, in particular to handle nested row structures.  Currently, the field is assumed to be part of a single row.
- [ ] Consider "scope parent" option?  (i.e. current collection and immediate parent, but no more)
- [ ] Add facility for import from RDF or SPARQL endpoint.
    - for each defined type, locate all records of that type (which are not also instances of a defined subtype), and use a SPARQL query to extract statements and format the results as JSON-LD.
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
- [ ] Views providing different perspectives on data; e.g. artifact centred, event centred, etc.  Would need a way to find inbound references as well as outbound.
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
    - [x] {{url:typeid/entityid}} URL for referenced entity.
    - [ ] {{ref:typeid/entityid}} link for referenced entity, using label from target.
    - [ ] {{field:typeid/entityid#property_uri}} field from referenced entity
- [ ] Think about how to incorporate resources from other collections by reference: feed into data bridges?
- [ ] Think about extending field descriptions to include:
    - [x] superproperty URIs (similar to supertype URIs in types)
    - [ ] rules that allow inferences of multiple RDF statements; e.g.
        ?a isRecordingOf ?b
        => 
        [ a frbroo:F29_Recording_Event ]
            frbroo:R20F_recorded ?b ;
            frbroo:R21F_created ?a .
    - the above pair might be combined.  We would then want to run the inferences when exporting JSON-LD
    - could this work on output like migration rules do on input?
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
    - make grid density a view option?
    - remove field placement values from field definitions?
- [ ] Rationalize common fields to reduce duplication?
    - but note that fields may use different comment/help text, so maybe not.
- [ ] introduce general validity checking framework to entityvaluemap structures (cf. unique property URI check in views) - allow specific validity check(s) to be associated with view(s)?  But note that general philosophy is to avoid unnecessary validity checks that might impede data entry.
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


----
