# Annalist TODO

NOTE: this document is used for short-term working notes; some longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] Add documentation for view Type, View, List and Group forms (similar to view Field ...)
- [ ] HOWTOs for common tasks; task-oriented documentation
    - Have tutorial; can this be used?
- [ ] Update tutorial to cover inheritance of definitions
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.
- [ ] New demo screencast(s)

# Version 0.1.37, towards 0.1.38

- [x] Absorb field groups into field defs
    - [x] modify field definition reader to use locally defined fields in preference to group reference
        - [x] in FieldDescritpion.py, use internal structure that is just a list of field id+property+placement from group def:
            - [x] Replace: group_view -> field_list
            - [x] Don't store group view in FieldDescription (store field list instead)
            - [x] Test and fix errors
            - [x] Update group_view_fields to return list if present
            - [x] field_desc.has_field_group_ref needs rework to align with refactoring
            - [x] if list is defined within field definition, use that
               - inlined repeat field definitions for type view
               - fix up resilience checks in entityedit.find_fields
               - remove unused group definitions
               - fix up test cases
            - [x] Rename: group_ids_seen -> field_ids_seen (recursion check)
    - [x] extend field definition view to include list of fields
        - [x] Add field Field_fields to field view
        - [x] Define field Field_fields, using field definitions from group Group_field_group
        - [x] Test, fix tests
        - [x] Eyeball changes by viewing type view fields 
            - Group_field_xxx options are not available in field view: need to complete next steps...
        - [x] Copy fields Group_field_sel, Group_field_property, Group_field_placement and rename references in Field_fields
        - [x] Test, fix tests
        - [x] Eyeball changes by viewing type view fields 
        - NOTE: at this stage, the Group_ref field is still present, allowing old-style definitions
    - [x] update site definitions to use field lists in field definitions
    - [x] eliminate field group definitions from site data
    - [x] modify or eliminate task buttons that create field group entities
    - [x] check for other uses of field group reference field
        - [x] entityedit.py save_invoke_task (task dispatching)
        - [x] fix up test cases
        - [x] entitylist.py get_list_entityvaluemap
        - [x] test_sitedata.py check_type_fields
        - [x] test_render_repeatgroup.py
        - [x] Test Define repeat field button in deployed software
            - [x] Define repeat field - button text mentions group
            - [x] Define repeat field - value type should be annal:Field_list
            - [x] Referenced field view - entity type field should be blank, or field list
            - [x] Field entity type help text mentions group
            - [x] Define repeat field - confirmation message mentions group; message needs refinement
        - [x] Test Define field reference button in deployed software
            - [x] Button text mentions group
            - [x] Default value type should be annal:Field_list
            - [-] Field entity type help text mentions group; sort out with separation of tooltip text
            - [x] Confirmation message mentions group; message needs refinement
            - [x] "Refer to type" has default type -> can this be inferred from target field?  Or prompt to specify value.
        - [x] fielddescription.py
    - [x] BUG (attempt to save copy of site label field):
            - Steps to reproduce:
                - Select scope all listing of entities
                - Select site entity
                - Click "edit" button
                - Enter new entity id
                - Click Save
            - Problem appears to be that the software is trying to copy the original entity data (as part of a rename operation) from the current collection rather than the collection from which it has been inherited.
        - [x] Handle change of collection like change of type: copy data to new location
            - [x] GET: copy original collection id to form as 'orig_coll'
            - [x] POST:
                - [x] extract orig coll id from form, default to current coll id
                - [x] save collection id information into DisplayInfo object
            - [x] DisplayInfo.__init__: initialize collection id values
            - [x] DisplayInfo.set_type_entity_id: set collection id values
            - [x] Refactor entityedit save_entity
            - [x] entityedit references to orig_type_id; also check orig_coll_id
            - [x] Need to be able to retrieve original collection type info for copy
            - [x] Check original collection access is honoured
                - [x] fairly extensive changes to EntityEdit and DisplayInfo logic to keep track of the (possibly inherited) collection from which an entity is accessed.
                - [x] Exposed a conflict with _user entity access; for now have added a hack in DisplayInfo.check_authorization, and added a new TODO (below) to implement a more principled interface to allow per-entity access controls.   Also have paper notes for cleaning up access control checks.
                - [x] Add test case for attempt to view/copy/edit entity inherited from collection with no access
            - [x] New test cases; edit inherited value with attachment
    - [x] entityedit.py - clean up dead code from previous refactoring
    - [x] check for other uses of RecordGroup class
        - [x] test_render_ref_multifields.py
        - [x] views/form_utils/fielddescription.py
    - [x] migrate group references in user field definitions to use internal field list
        - [x] Add logic to RecordField to import field definitions from group definition
        - [x] Warning on migration if value type of repeat field does not match type of referenced group
        - [x] Add optional deprecation warning when recordgroup is instantiated (except for migration)
            - NOTE: EntityTypeInfo scans suppress these warnings, as they're used by migration logic
        - [x] Above changes should mean all live references are to inline field list
        - [x] Add _group rename to collection migration function
    - [x] test migration functionality
        - [x] Add test case to test_data_migration
    - [x] apply migrations to installable collections
        - Install software then use annalist-manager commands to apply migrations;
        - Check, and copy migrated data back to source tree
        - [x] Annalist_schema (should be no change)
        - [x] Bibliography_defs (done by hand)
        - [x] Concept_defs
        - [x] Journal_defs
        - [x] RDF_schema_defs
    - [x] eliminate group definitions in installable collections
        - [x] Annalist_schema
        - [x] Bibliography_defs
        - [x] Concept_defs
        - [x] Journal_defs
        - [x] RDF_schema_defs
    - [x] seek out other references to RecordGroup class
    - [x] annalist-manager option to migrate all collections
    - [x] fix up installable collection problems picked up by collection migration 
    - [x] Remove field group from field view definition
    - [x] Update field view help text to mention subfields, not field group
    - [x] seek out other references to field group type name or URI
        - NOTE: references to group type, views, lists remain for migration support, and free-standing view and list definitions, remain -- for now.

- [.] Fix handling of restriction expression for subfield selection.
    [x] Need test case coverage for subfields in field defintion, and domain and/or range classes in RDF_schema (e.g. _field/subpropertyOf on _field/subpropertyOf_r)
    [x] In FieldListValueMap, add {'group': field_desc_dict} to extra value context.
        - Should be accessible in restriction expression as 'field[...]'
    [-] Update view help text to mention "field". 'field[<field-id>]' references subfields 
        contained within a containing field, refers to a component of the containing field 
        description.  (Turns out this wasn't needed - consider removing it?)
        Extra logic is in FieldListValueMap handling of field lists.

- [ ] Annaslist_schema add annal:field_fields property
- [ ] annalist.namespace - default to CURIE, use .URI for URI.  Affects JSON-LD context test.
- [ ] Provide field popup help separately from comment field (without MarkDown)
    - [ ] Add new property URI to ANNAL namespace
        - annal:tooltip
    - [ ] Add new field; change label on comment field
    - [ ] Default to rdfs:comment value if blank
    - [ ] Add migration logic to copy comment
    - [ ] Edit sitedata field definitions
- [ ] Split Resource_defs from Journal_defs?
- [ ] Update installed software on fast-project.analist.net
    - (waiting for confirmation from Mat that data is OK)

(feature freeze for V0.9alpha?)
(0.5?)

- [ ] Fix user access permission hack for copying inherited default user (see DisplayInfo.check_authorization)
- [ ] How to deal with reference to entity that has a permanent URI defined (per annal:uri)?
    - Currently, reference is internal relative reference, but for exported linked data the permanent URI should be used (e.g. references to concept tags or types).
    - If absolute URI is stored, can local reference be discovered for hyperlinking?
    - I think evolvability is served by making these exchangeable
- [ ] Login sequence from authz error page does not return to original page viewed
- [ ] Figure out how to preserve defined users when reinstalling the software.
    - I think it is because the Django sqlite database file is replaced.  Arranging for per-configuration database files (per above) might alleviate this.
    - Seems to be working, but needs explicit testing to make sure.
- [ ] update Django version used to latest version designated for long term support (1.8?)
- [ ] update pip to latest version in python environment (for continued testing)
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] deploy `letsencrypt` certs on all `annalist.net` servers and force use of HTTPS.
        - [ ] Document setup process.
    - [ ] Check out https://docs.djangoproject.com/en/1.8/ref/django-admin/#django-admin-check
    - [ ] Shared/personal deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [ ] "Type definition" help text is a little confusing (cf 'Entity types ...').
- [ ] Eliminate type-specific render types (i.e. 'Type', 'View', 'List', 'Field', etc.), and any other redundant render types.  Also "RepeatGroup" and "RepeatGroupRow".
- [ ] Remove surplus fields from context when context generation/migration issues are settled
    - cf. collection.set_field_uri_jsonld_context, collection.get_coll_jsonld_context (fid, vid, gid, etc.)
- [ ] Render modes:  instead of a separate function for each mode, pass parameter to each renderer and select at the point of rendering (e.g. see render_fieldvalue.render_mode)
    - this should avoid the need for the multiple layers of wrapping and duplication of render mode functions.  Field description should carry just a single renderer; figure later what to do with it.)
- [ ] In render_select.py: remove references to {{field.field_value}} and {{field.field_value_link_continuation}} and use locally generated {{field_labelval}}, etc.
    - [ ] The continuation URI will need to be provided separately in the context (via bound_field?) and mentioned separately in the templates.
    - [ ] Remove corresponding special case code in bound_field.
- [ ] The handling of entity_id and entity_type involves some special case testing in bound_field, due somewhat to the early template-based logic for field rendering.  With the introduction of separate render-templates in views.fields.render_select.py, it may be possible to change the context variables used for this case and remove the special logic in bound_field.
- [ ] Similar to above for entity_id, except that it uses a separate template in templates.fields.
- [ ] Can annal:field_name in field descriptions be eliminated with revised entity_id and entity_type logic?
- [ ] *delete views: rationalize into single view?
- [ ] performance tuning
    - [ ] in EntityTypeInfo: cache type hierarchy for each collection/request; clear when setting up
    - [ ] look into entity cacheing (esp. RecordType) for performance improvement
        - partly done per-collection - is this enough?
    - [ ] Re-think access to entities and types:
        - [ ] There is repeated reading of RecordType values in EntityFinder
              (cf. collection.types() and EntityTypeInfo constructor; also URI access)
        - [ ] Need more direct way to locate type (and other entities?) by URI
        - [ ] Review common mechanism to retrieve URI for entity?  
              (Current mechanism fixes use of annal:uri for all entities; maybe OK)
        - [ ] Think about how to optimize retrieval of subtypes/supertypes
        - [ ] Do special case for types, or more generic caching approach?
- [ ] review renderers and revise to take all message strings from messages.py
- [ ] review title/heading strings and revise to take all message strings from messages.py
- [ ] entityedit view handling: view does not return data entry form values, which can require some special-case handling.  Look into handling special cases in one place (e.g. setting up copies of form values used but not returned.  Currently exhibits as special handling needed for use_view response handling.)
- [ ] entityedit view handling: refactor save entity logic to follow a pattern of extract, validate, update in separate functions so that these can be recombined in different ways.  Note effect on `save_invoke_task` method, and elsewhere.
- [ ] Review nomenclature, especially labels, for all site data
- [ ] Provide content for the links in the page footer
- [x] Remove dependency of annalist-manager on test-suite-generated data when creating/updating site
    - copy site data in directly from `sitedata`
    - generate all other site data on-the-fly as needed (e.g. context, etc.)
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
- [ ] See_also_r field duplicated in field options list?
    - [ ] Entity_see_also_r duplicates label also used in Journal_defs/See_also_r (?)
        - What uses Entity_see_also_r?  Is this needed?  Can it be sensibly relabelled or removed?  
            - RDF_schema_defs/_view/Class
            - _view/Vocab_view
        - Or can Journal_defs use Entity_see_also_r ?  [Maybe - check definition and delete Journal_defs version if no difference]
        - Tried changing Journal_defs See_also_r to use Group_set_row render type: maybe this will be enough?  IT MAY BE ENOUGH TO PREVENT CLASHES WHEN GENERATING A CONTEXT, BUT THE DIFFERENT DEFINITIONS REMAIN.  Change label for one?  Use same id for both?

Technical debt:

- [ ] Implement in-memory entity storage to speed up test suite, and lay groundwork for LDP back-end
- [ ] Move top menu selection/formatting logic from template into code (e.g. context returned by DisplayInfo?)
- [x] Rework Bib_* definitions/enumerations so that they don't need special mention in EntityInfo
- [x] Consider treating Enum types as regular types under /d/?
- [x] Field layout padding logic at end of row is dependent on height of edit fields; consider re-working this in `fieldlistvaluemap` to generate fields in groups, where each group is rendered as a separate row.
- [ ] Built-in type id's: use definitions from `models.entitytypeinfo` rather than literal strings
- [ ] Consider `views.site`, `views.collection` refactor to use `views.displayinfo`
- [ ] Implement "get the data" link as a field renderer?
- [ ] Consider eliminating the /c/ directory (but provide redirects for link compatibility/coolness)
- [ ] review view URL returned for entities found with alternative parentage:
    - currently force URL returned to be that of original parent, not alt. 
    - This is done to minimize disruption to tests while changing logic.
    - See: _entityviewurl member variable
    - logic is handled in `Entity.try_alt_parentage` and _init_child`
    - may want to consider promoting entityviewurl to constructor parameter for all Entity.
- [ ] Delay accessing settings data until actually needed, so that new dependencies (e.g. models on views) don't cause premature selection.  This will help to avoid certain unexpected problems cropping up as happened with release 0.1.22 logging setup for annalist-manager.
- [ ] After reworking site data access, review `layout.py` and patterns for accessing entities, metadata, context data, etc.
    - The various relative references for accessing context data are particularly unclear in the current software.
- [ ] Inconsistent `@id` values in site data
- [ ] "Customize" view style getting out of sync with other page styles
    - possible enhancements to form generator to generate customize page using form logic?
- [ ] Refactor entity edit response handling
- [ ] Review handling of composite type+entity identifiers in list display selections to bring in line with mechanisms used for drop-down choicess.
- [x] The field rendering logic is getting a bit tangled, mainly due to support for uploaded files and multiple field references to a linked entity.  Rethinking this to maintain a clearer separation between "edit" and "view" modes (i.e. separate render classes for each) should rationalize this.  The different modes require multiple methods on different modules in different classes;  can the field description have just 2 renderer references (read/edit) and handle the different modes from there?  (It is field description values that are referenced from templates.)
- [ ] Check EntityId and EntityTypeId renderers appear only at top-level in entity view
- [ ] Installable collection metadata: read from collection directory (currently supplied from table in "annalist.collections")


Data collection definitions:

- [ ] VoID, DCAT, PROV


Usability notes:

- [ ] Select+"edit" from list display uses list-defined view, not entity type view as when hyperlink is clicked
- [ ] Deprecate "Refer to field" field in field view, and "Field reference" value mode. 
- [ ] Continuation from login is sometimes/often lost (provide example)
- [ ] Task button option to copy type+view+list and update names and URIs
    - problems:
        - how is the new type name defined?  (Also the new view and list.)
        - should edits to the current type be saved first?
    - implementation deferred until save entity logic in `entityedit.py` has been refactored: follow a pattern of extract, validate, update in separate functions so that these can be recombined in different ways.
- [ ] Group value type: use target type for @id fields, but also allow intermediate types (e.g., for prov:qualifiedAssociation -> prov:Association).  Check how this plays with changes made in previous release per Mat's comment.
    - group target type field is used for field selection - should default to type of containing entity or new type.  Referenced type is not relevant there.
    - not seeing the problem here: revisit when problem surefaces again.
- [ ] If logout results in loss of authorization to view resource, go to collection view?
    - This could be tricky, as each view does its own auth checks.
    - Would need much better structuring of view dispatching to enable pre-flight auth check.
    - As an edge case, dopn't worry about this immediately.
- [ ] Add menu bar link to display content of collection rather than default
    - List of types, linked to lists?
- [ ] Try to make changing entity type and entity id follow-through more smoothly.
    - especially when creating a supertype and selecting an appropriate subtype.
- [ ] Better support for type renaming: hunt out all references and rename them too
- [ ] Consistency checks for references to missing types (e.g. following rename)
- [x] Display entity-id *and* label values in drop-downs?  (e.g. "id (label)")
- [ ] Simplified field-definition interface? (hide confusing detail; use javascript to hide/expose fields based on selection from simple enumeration of field types?)
- [ ] Persist item selection to refreshed display when move-up/movedown clicked?
- [x] Easy(er) switch to alternative views (e.g. manufacture, performance for Carolan events)
- [x] OR... allow an entity to specify its own default view? (this is now handled by subtyping)
- [x] Type/List/View dropdowns: normally show only those types/lists/views defined by the current collection, but ensure it is still reasonably easy to get lists of built-in types as well.  Details need to be worked out.
- [x] View forms need title (indicating type of thing viewed)?  Or let user define label for Id field?
- [x] Provide field type that can be used to place fixed annotations/instructions in a form
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
- [x] Option to re-order fields on view form
- [ ] When creating type, default URI to be based on id entered
- [ ] List display paging
- [ ] When generating a view of an enumerated value, push logic for finding link into the renderer, so that availability of field link does not depend on whether field is available for the selected view.  (Try changing entity type of field to random value - can no longer browse to field description from view/group description)


Notes for Future TODOs:

(Collecting ideas here: consider expand them in the GitHub issues list.)

- [ ] Final elimination of Recordroup (field group) entities
    - [ ] Remove class RecordGroup
    - [ ] eliminate _field/Field_groupref instances
    - [ ] eliminate _view/Field_group_view, _list/Field_group_list
    - [ ] eliminate all Group_* fields
    - [ ] Remove field group type URI from annal: namespace
    - [ ] eliminate _type/_group
    - [ ] Remove '_group' from EntityTypeInfo dispatching tables
    - [ ] Clean up dead code:
        - [ ] test_recordfield.py

- [ ] Review how URIs are generated for referenced entities: currently a relative reference is used, which resolves to a local URL for the entity concerned.  But if the entity has a global identifier (`annal:URI`) that that should appear in exported data.  One fix is to just use global URIs in text fields when global URIs are expected (e.g. supertypes in class description).  E.g., consider generating:
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
        -   http://support.orcid.org/knowledgebase/articles/343182-register-a-public-api-client-application
        -   http://members.orcid.org/api/introduction-orcid-public-api
    - [ ] Other OpenID Connect providers; e.g. see http://openid.net/certification/
        - hard to find actual provider service other than Google
    - [ ] https://aarc-project.eu
    - tried investigating EUDat, which looks promising but fails with invalid certificate
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
- [ ] From view of list definition, link to show list itself
    - Beside "Show view" button, add "Show list"?
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
- [x] Collection metadata editing requires site-level permissions; 
    - to apply collection level permissions wout require entity level access control settings
    - think about this?
    - see EntityTypeInfo.__init__
- [ ] Introduce site-local and/or collection-local CSS to facilitate upgrades with local CSS adaptations.
- [ ] Issues raised by Cerys in email of 23-Oct-2015.  Some good points there - should break out into issues.
- [ ] consider render type option for repeat group rows without headings? (simple repeat group doesn't hack it).
    - Should be easy to add.  Just need a name.
- [ ] Scrolling through views from list - e.g. Next/Prev item buttons? (Iris G)
- [ ] Option to scan for broken entity references (e.g., due to removal, renaming)
- [ ] Extend task definitions to include validation: allow error reporting
- [x] Allow comment field to be left blank and use label instead?  Maybe not: later, allow comment field to default to label.
- [x] field renderer for unified import or upload resource?
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
- [x] Provide a way to edit collection metadata (e.g. link from Customize page)
- [x] Provide a way to edit site metadata
- [x] Provide a way to view/edit site user permissions
- [x] Provide a way to view/edit site type/view/list/etc descriptions
    - Not edit: site data should be stable and controlled.
    - Provided collection structure inheritiance instead.
- [ ] Undefined list error display, or any error - include link to collection in top bar
- [x] Help display for view: use commentary text from view description; thus can tailor help for each view.
- [x] Use markdown directly for help text
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


# Feedback

* https://github.com/gklyne/annalist/issues/40


----
