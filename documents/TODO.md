# Annalist TODO

NOTE: this document is used for short-term working notes; some longer-term planning information has been migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


# Documentation

- [ ] Add documentation for view Type, View, List and Group forms (similar to view Field ...)
- [ ] HOWTOs for common tasks; task-oriented documentation
    - Have tutorial; can this be used?
- [ ] Update tutorial to cover inheritance of definitions
- [ ] Review concurrent access issues; document assumptions
    - original design called for copy of original record data to be held in form, so that changes could be detected when saving entity; also, allows for "Reset" option.
- [ ] New demo screencasts


# Version 0.1.25, towards 0.1.26

- [ ] BUG: uploading PDF as image results in file extension PNG
    - [x] new resource type aded, but still needs testing
    - [ ] consider using different default extension?
- [ ] Home page: change button labels: "view metadata", "edit metadata", "remove collection".
    - Add renderers for view short text and view markdown.
- [ ] Collection edit metadata page: make s/w version display-only.
- [ ] Content negotiation on entity URI for alternative formats (initially just HTML (form), JSON-LD); others later.
- [ ] annalist-manager options to copy Bibliographic and maybe other built-in collection data
- [ ] Create schema definitions in Annalist for ANNAL namespace
- [ ] When supertypes are changed, need to regenerate @type fields of instances, or be smarter about how entries for listing are selected.  Link to migration?
- [ ] Think further about how data migration can be handled.  E.g. several properties used in the Carolan Guitar data look inappropriate when viewed as JSON-LD: there should be a way to rename the properties *and* migrate the data. (Combine existing migration and alias logic?)
- [ ] In drop-down list, try including typeid/entityid only for entries whose labels are not unique.
- [ ] Form field layout: introduce padding so the fields lay out as indicated by the position value.  Add field padding so that display position is as expected (if possible)
    - RenderFieldValue.label_view and .label_edit seem to be the key functions.
    - How to carry context forward?
    - Possibly precompute padding?
        - This would require logic in fieldlistvaluemap, fielddescription and render_placement
        - plus new logic to render the padding elements
    - Another option: take field-loop out of template and run it as a `render_all_fields` method
        - still needs placement parser to return position+width information
- [ ] Provide collection overview that allows to see users what is present
    - initially, just provide a "What's here" list that displays default list label for all types + link to display list.
    - long term, this might be a high-level graphical display (like PROV diag.)
- [ ] Add "CodeArea" field type for unflowed, unformatted text with non-propo font
- [ ] Review URI usage
    - [x] avoid explicit reference to `_analist_collection`?
    - [ ] review base URI designation in JSON-LD:
        - note `@base` ignored if used in external contexts;
        - can specified value be relative? YES:
            - [syntax sect 8.7](http://www.w3.org/TR/json-ld/#context-definitions) and 
            - [API sect 6.1](http://www.w3.org/TR/json-ld-api/#context-processing-algorithm) para 3.4
        - Add `@base` to generated entity data:
            - Using `(site_base)/c/(coll_id)/d/` as base URI would mean that entity ids (`type_id/entity_id`) work directly as relative URIs.  
            - Also `type_id` to retreive a list of entities of that type.
            - Thus use `{ "@base": "../..", @context": "@context", ... }` in entity data.
        - at the time of writing, there is a problem with rdflib-jsonld base URI handling; for now, avoid use of @base.  This means that entity references treated as URIs are not handled as expected, hence for now are stored as literals, wghich means these links are not directly visible in RDF.
            - cf. https://github.com/RDFLib/rdflib-jsonld/issues/33
    - [ ] collections and repeated properties:
        - Using owl:sameAs in form { "owl:sameAs" <some_resource> } as equivalent to just <someresource>.
        - could use `@id`?

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
- [ ] implement at least one other identify provider (ORCID?)
- [ ] annalist-manager options for users, consider:
    - [ ] annalist-manager createlocaluser [ username [ email [ firstname [ lastname ] ] ] ] [ CONFIG ]
    - [ ] annalist-manager setuserpermissions [ username [ permissions ] ] [ CONFIG ]
- [ ] Remove all references to `field_target_type` - where needed, use `field_value_type` instead.

(feature freeze for V0.9alpha?)
(0.2?)

- [ ] update Django version used to 1.8 (designated for long term support)
- [ ] review renderers and revise to take all message strings from messages.py
- [ ] look into entity cacheing (esp. RecordType) for performance improvement
- [ ] entityedit view handling: view does not return data entry form values, which can require some special-case handling.  Look into handling special cases in one place (e.g. setting up copies of form values used but not returned.  Currently exhibits as special handling needed for use_view response handling.)
- [ ] Review nomenclature, especially labels, for all site data
- [ ] Eliminate type-specific render types (i.e. 'Type', 'View', 'List', 'Field', etc.), and any other redundant render types
- [ ] Provide content for the links in the page footer
- [ ] Security and robust deployability enhancements [#12](https://github.com/gklyne/annalist/issues/12)
    - [ ] deploy `letsencrypt` certs on all `annalist.net` servers and foce use of HTTPS.
        - [ ] Document setup process.
    - [ ] Check out https://docs.djangoproject.com/en/1.8/ref/django-admin/#django-admin-check
    - [ ] Shared/personal deployment should generate a new secret key in settings
    - [ ] Need way to cleanly shut down server processes (annalist-manager option?)
    - [ ] See if annalist-manager runserver can run service directly, rather than via manage.py/django-admin?
- [x] Remove dependency of analist-manager on test-suite-generated data when creating/updating site
    - copy site data in directly from `sitedata`
    - generate all other site data on-the-fly as needed (e.g. context, etc.)
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
- [ ] Review docker files: reduce number of separate commands used; always build on clean python setup
- [ ] Code and service review  [#1](https://github.com/gklyne/annalist/issues/1)
- [ ] Simplify generic view tests [#33](https://github.com/gklyne/annalist/issues/33)
- [ ] Review length restriction on entity/type ids: does it serve any purpose?
- [ ] Checkout default form buttons. See:  http://stackoverflow.com/questions/1963245/multiple-submit-buttons-on-html-form-designate-one-button-as-default/1963305#comment51736986_1963305
- [ ] Move outstanding TODOs to GitHub issues


Technical debt:

- [ ] Implement in-memory entity stiorage tio speed up test suite, and lay groundwork for LDP back-end
- [ ] Built-in type id's: use definitions from `models.entitytypeinfo` rather than literal strings
- [ ] Consider `views.site`, `views.collection` refactor to use `views.displayinfo`
- [ ] Implement "get the data" link as a field renderer?
- [ ] Consider treating Enum types as regular types under /d/?
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
- [ ] `annal:Slug` for entity references - is now type/id: rename type?  (annal:Entity_ref?)
- [ ] Inconsistent `@id` values in site data
- [ ] Re-think access to entities and types:
    - [ ] There is repeated reading of RecordType values in EntityFinder
          (cf. collection.types() and EntityTypeInfo constructor; also URI access)
    - [ ] Need more direct way to locate type (and other entities?) by URI
    - [ ] Review common mechanism to retreive URI for entity?  
          (Current mechanism fixes use of annal:uri for all entities; maybe OK)
    - [ ] Think about how to optimize retreival of subtypes/supertypes
    - [ ] Do special case for types, or more generic caching approach?
- [ ] Customize view getting out of sync with other page styles
    - possible enhancements to form generator to generate custoimize page using form logic?
- [ ] Refactor entity edit response handling
- [ ] Review handling of composite type+entity identifiers in list display selections to bring in line with mechanisms used for drop-down choicess.
- [ ] In render_select.py: remove references to {{field.field_value}} and {{field.field_value_link_continuation}} and use locally generated {{field_labelval}}, etc.
    - [ ] The continuation URI will need to be provided separately in the context (via bound_field?) and mentioned separately in the templates.
    - [ ]remove corresponding special case code in bound_field.
- [x] The field rendering logic is getting a bit tangled, mainly due to support for uploaded files and multiple field references to a linked entity.  Rethinking this to maintain a clearer separation between "edit" and "view" modes (i.e. separate render classes for each) should rationalize this.  The different modes require multiple methods on different modules in different classes;  can the field description have just 2 renderer references (read/edit) and handle the different modes from there?  (It is field description values that are referenced from templates.)
- [ ] The handling of entity_id and entity_type involves some special case testing in bound_field, due somewhat to the early template-based logic for field rendering.  With the introduction of separate render-templates in views.fields.render_select.py, it may be possible to change the context variables used for this case and remove the special login in bound_field.
- [ ] Similar to above for entity_id, except that it uses a separate template in templates.fields.
- [ ] Can annal:field_name in field descriptions be eliminated with revised entity_id and entity_type logic?
- [ ] Check EntityId and EntityTypeId renderers appear only at top-level in entity view


Usability notes:

- [ ] Make login screen clearer (cf. email from Iris 06/10/2015 16:15)
- [ ] Display entity-id *and* label values in drop-downs?  (e.g. "id (label)")
- [ ] Simplified field-definition interface? (hide confusing detail; use javascript to hide/expose fields based on selection from simple enumeration of field types?)
- [ ] Persist item selection to refreshed display when move-up/movedown clicked?
- [x] Easy(er) switch to alternative views (e.g. manufacture, performance for Carolan events)
- [x] OR... allow an entity to specify its own default view? (this is now handled by subtyping)
- [ ] Type/List/View dropdowns: normally show only those types/lists/views defined by the current collection, but ensure it is still reasonably easy to get lists of built-in types as well.  Details need to be worked out.
- [ ] View forms need title (indicating type of thing viewed)?  Or let user define label for Id field?
- [ ] Provide field type that can be used to place fixed annotations/instructions in a form
- [ ] Add title attributes to all buttons - used as tooltip
- [ ] Add title to field controls based on field help, to use as tooltip.
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
- [ ] Use pop-up text based on field comment to tell user how a field value is used
- [x] Option to re-order fields on view form
- [ ] When creating type, default URI to be based on id entered
- [ ] Instead of separate link on the login page, have "Local" as a login service option.
- [ ] List display paging
- [ ] When generating a view of an enumerated value, push logic for finding link into the renderer, so that availability of field link does not depend on whether field is available for the selected view.  (Try changing entity type of field to random value - can no longer browse to field description from view/group description)


Notes for Future TODOs:

(Collecting ideas here: consider expand them in the GitHub issues list.)

- [ ] Collection metadata editing requires site-level permissions; 
    - to apply collection level permissions wout require entity level access control settings
    - think about this?
    - see EntityTypeInfo.__init__
- [ ] Introduce site-local and/or collection-local CSS to facilitate upgrades with local CSS adaptations.
- [ ] Issues raised by Cerys in email of 23-Oct-2015.  Some good points there - should break out into issues.
- [ ] consider option for repeat group rows without headings? (simple repeat group doesn't hack it).
    - Should be easy to add.  Just need a name.
- [ ] Scrolling through views from list - e.g. Next/Prev item buttons? (Iris G)
- [ ] Option to scan for broken entity references (e.g., due to removal, renaming)
- [ ] Extend task definitions to include validation: allow error reporting
- [ ] Allow comment field to be left blank and use label instead?  Maybe not: later, allow comment field to default to label.
- [ ] field renderer for unified import or upload resource?
- [ ] `annal:member` - used to "lift" repeated values to the property that references a repeat group?
    - e.g. see /annalist/c/Carolan_Guitar/d/_field/Event_r/
    - DOES NOT WORK:  if used to reference group, can only have one repeat group; if used to reference item, cannot use item field in isolation.
    - Options (#1 looking favourite):
        1. use same property for group and field; recognize and elide when generating/reading RDF?
        2. use auto-generated unique property for group ref.  Can recognize for RDF?
        3. group description to use 'annal:member' property override
    - IMPLEMENTING: use `owl:sameAs` for singleton dictionaries in a JSON list.
        - equivalent to `[ owl:sameAs <some_resource> ]`
        - (could use `@id` has key ?)
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
- [ ] SPARQL data bridge: use combination opf SPARQL CONSTRUCT query + JSON-LD frame?
- [ ] View selection based on pattern match; e.g. JSON PATCH "Test" operation.
- [ ] git/github integration
    - [ ] annalist-manager options to load/save collection using git (assuming git is installed)
    - [ ] internal options to save history in per-collection git repo


# Feedback

* https://github.com/gklyne/annalist/issues/40


----
