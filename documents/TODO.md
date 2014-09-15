# Annalist TODO

   - proposed activity
   > in progress
   / completed
   x rejected
   * additional note

NOTE: information in this document is being migrated to [Github issues](https://github.com/gklyne/annalist/issues) and a [roadmap document](roadmap.md).


## Initial web application outline plan

Initially guided by mockups per https://github.com/gklyne/annalist/tree/develop/mockup

1. Front page/initial display
   / form elements to create new collection
   / form elements to delete collection
   / include supporting logic in Collection module
   / rework authentication/authorization to allow unauthenticated access for public data 
   / test cases for site, site views; refactor tests to separate directory, modules
   / adopt responsive CSS framework (Foundation)
2. Collection display
   / refactor metadata field access to common superclass
   / types
     / implement skeleton RecordType module
     / create test cases for types in collection
     / implement type methods
   / views
     / implement skeleton RecordView module
     / create test cases for views in collection
     / implement view methods
   / lists
     / implement skeleton RecordList module
     / create test cases for lists in collection
     / implement list methods
   / UI test cases
   / form elements to add/delete types/views/lists/...
   / Add CollectionActionView test cases (handled with entity managed)
3. Record type display
   / template
   / view: edit form display
   / view test cases
   / refactor redirect_info, redirect_error in generic view to takle URI rather than view name parameter,
     and add new method to handle URI generation from view name + params.
   / model
   / model test cases
   / view edit form response handling
   / refactor code locally
   / more refactoring; try to abstract common logic for RecordList, RecordView
   / review generic view base functions - should some be inlined now?
   / Move types/views/lists data into _annalist_collection directory
4. Default record view/edit display (code to be refactored later)
   / form generation
   / form display test cases
   / provision for data access fallback to site data (for types, views, fields, etc.)
   / form response handler
   / test cases
   / refactor URI and test data support for test cases to separate module; use reverse for URI generation; 
   / refactor DefaultEdit form display
   x isolate directory generation for tests.
   / change <site>/collections/ to <site>/c/ or <site>/coll/ throughout.
   x Similar for /d/ and /data/?
   / include path values in entities.
   x include base and reference values in entities. (later: requires use of @context)
   / create data view display based on generic render logic
   / editing recordtype: returns "already exists" error; display operation (new, copy, edit, etc) in edit form
   / function to create initial development site data (based on test code)
   x entity should carry its own RecordType id (where it's kept within a collection).  Have implemented alternative mechanism through bound_field that allows the entity to be less self-aware, hence more easily ported.
   / menu dropdown on small display not working: need JS from Zurb site? (fixed by update to 5.2.1)
5. Default record list display
   / form generation
   / form display test cases (initial for default and all)
   / include sitedata lists in drop-down
   / form response handler (delete and others todo)
   / entity list view: add selection fields (and classes)
   / form response test cases
   / customize response handler
   / new entity from list-all display; changing type of entity
       / Create default type in site data
       / Create field render type for drop-down (render_utils and field template)
       / Add field to default display
       / Add type list data to display context
       / Add original type as hidden field in edit form
       / Add logic to form submission handler
       / add test cases for changing type id (new and edit)
       x remove recordtypedata access from entityeditbase.get_coll_type_data to POST handler (for recordtype, etc., the collection object is supplied as parent, so this is not so simple.)
       / remove return_value from field definitions - this is now handled differently
       / new record from list all: use default type, not random selection
       / new record, change type, error doesn't redisplay types
       / error loses continuation URI in edit form
       / remove message header that appears on return from form edit (appears to be resolved?)
       / review skipped tests - can any be enabled now?
       / delete entity continues to wrong page
   / add entity links to list views
       / Update bound_field to provide access to entity URI
       / Create field render type for entity ref
       / Update field in default list displays
   / connect site display to default display of entities, not customize
   / connect list display to record view display
   / build entity selector logic into list view
6. Generic entity edit view
   / extract/generalize relevant logic from `defaultedit.py`
   / parameterize view-id on extra URI field
   / create new URI mapping entries
   / create new test suite for generic edit view
   / refactor defaultedit.py as special case (subclass?)
   / fix urls.py error and re-test
7. Generic record list display and editing
   / extract/generalize relevant logic from `defaultlist.py`
   / refactor defaultlist.py as special case (subclass?)
   / parameterize view-id on extra URI field
   / create new URI mapping entries
   / create new test suite for generic list view
     / choose test scenario: Field definitions: http://localhost:8000/annalist/c/coll1/d/_field/ 
     / list field descriptions?  Need to create list description (4 fields?).
       http://localhost:8000/annalist/c/coll1/l/Fields_list/_field/
     / also choose / define default view for list (Create field view?)
     / need to rationalize entity display structure to encompass data, collection level metadata and site-level metadata.
     / check list display in dev app
     / define test suite test_genericentitylist based loosely on test_entitydefaultlist
     / create test case for creating/editing site metadata entities (currently fail in dev system) e.g. create test_entitymetadataedit based on entitygenericedit.
     / create edit view tests for all the main entity classes (type, view, list, data), 
       along the lines of test_entityfieldedit, moving support code out of entity_testutils.
       / copy/refactor test_recordtype to use same pattern as test_entityfieldedit
       / see if old record type view class can be deleted
       / incorporate model tests in test_entityfieldedit (cf. test_recordtype)
       / rename test_entityfieldedit -> test_recordfield? (cf. test_recordtype)
     / resolve overloading of "entity_uri" in context.  In `entityeditbase.py:58` it is taken from
       `annal:uri`, but in `render_utils.py:108` it may be derived from the entity object, not the data
       via logic at `entityroot.py:119` (.set_values()).
       This leads to inconsistency with metadata entities.  What value *should* be returned for these:
       the actual location or the URI used for viewing?  Ideally, we'll use the `/c/coll/d/_type/id`
       form, as that hides whether it comes from the collection or is site-wide.
   / entity_uri appears in entity view context as name (same as annal:uri) but also in bound field as locator.  Change name used in bound field to `entity_ref`.
   / refactor delete confirm code to generic module, with type-specific messages.  Note that type, view and list deletes are triggered from the collection edit view, with different form variables, and also have specific remove functions in the collection class, so need separate implementations (for now?).
   / update render template/logic for RecordView_view
   / update template to include delete field options; finalize form response data
   / implement tests for add/delete fields
   / implement handlers for add/delete fields
   / edit form response should update, not replace, any data from the original (so data from multiple views is not discarded).
   / implement delete confirm view for views and lists.
   / review missing tests: implement or delete?
   / fix up view links from list display
   / define View-list and List-list
   / view button handler from list display + test
   / continuation handling: replace by more generic parameter handling based on dictionary; move handling of escape logic, etc.
   / search button handler from list display
   / consider that 'Find' and 'View' buttons could be combined
   / don't include continuation-uri param when URI is blank
   / implement some version of entity selection logic
   / decide how to handle presentation of field types (where?):
     (a) use simple text string, not CURIE
     (b) use CURIE, but use render type to extract ID; but will need to map back when form is submitted?
     / it all rather depends on the anticipated extensibility model for field types.
       Option (a) is simplest for now.
   / default_view response handler (needs generic view to make sense)
   / implement view- and list- edit from collection customization page
   / implement per-type default list and view
     / already works for list view; e.g. http://localhost:8000/annalist/c/coll1/d/_type/
     / but not yet for entity view; e.g. http://localhost:8000/annalist/c/coll1/d/_type/type1/
     / return list_info structure rather than saving values in object. 
   / consider replicating list_seup logic for view_setup.
   / find and eliminate other references to get_coll_data, etc.
   / don't return placeholder text in a form as field value; use HTML5 placeholder attribute
   / refactor fields package as subpackage of views
   / fix entity links to use default view URI (/d/...)
   / List type + "View" selection uses // for type field - select based on list or suppress
   / customize > edit record view > add field > cancel -- returns to wrong place.
   / need test case for remove field with no field selected
   / factor out add-field logic used by current add-field code
   / test case for POST with 'add_view_field'
   / provide option to invoke add-field logic during initial form rendering
   / add_field button on entity edit displays; need way to control its inclusion
   / new entity initialization vector through typeinfo, AND/OR provide mechanism to associate initial values for each entity type.
   / "Add field" when creating new entity results in multiple entities created (use !edit for continuation URI?)  Add test case.
   / tests
     / skipped '@@TODO defaultlist default-view button handler'
     / skipped '@@TODO defaultlist search button handler'
     / skipped '@@TODO genericlist default-view button handler'
     / skipped '@@TODO genericlist search button handler'
       / annalist.tests.test_entitygenericlist.EntityGenericListViewTest
     / skipped '@@TODO genericlist default list button'
       / annalist.tests.test_entitygenericlist.EntityGenericListViewTest
8. initial application testing
   / review and simplify bound_field logic for accessing field_value
   / Create new type - appears twice in default_list_all display.  Delete one deletes both appearances, so this looks like display problem.  I thought this had been fixed.  Confirmed to be knock-on from incorrect creation of _type data (see next).
   / New entry save as _type does not create new type in collection
   / field view has size/position field; use as default when adding to view.
   / viewing new entity with custom type generates "keyerror annal:value_type" @ fielddescription.py line 55.
   / (a) update field view description to display all relevant fields; ???
   / (b) when defining a field, the render type selected also implies a field value type; handle this in "FieldDescription constructor?"  Later, maybe.  For now, add value type field.
   / (c) make FieldDescription constructor more resilient to missing data.
   / Changing type to built-in type in entity edit display does not save to correct location
   / List editing view formatting is messed up (small-6?)
   / Click on local type in default_list, then cancel, returns to Type_list display.  No continuation_uri in links.
   / Click on local record in Default_list, cancel, returns to default data display (/d/ rather than /l/).  In default display, types don't appear.
   / grey out set_default button on collection default display (/d/, /l/)
   / When creating new collection, there's no obvious way to create a new record type (or view).
   / Handle bare /l/ URI and redirect to default view for collection
   / Remove precalculated list_ids and view_ids from view context
   / Script to refresh sitedata in devel site
   / In view editing, provide field id drodown
   / In list displays, hyperlink entity type to view/edit form
   / No easy way to create field description while editing view details; include new-field button
       / update form template
       / implement handler for 'new_field' response
       / implement test case for 'new_field' response
       / list description view not showing types or views in dropdowns
       / introduce Default_field type
   / When defining field, missing placement is silently ignored; field is not saved; (still)
   / Authorization of field editing is not handled consistently:
     allows config when no delete authz (no login)
     Also, display of remove-field checkbox is based on "delete" permission. 
   / Save entity edit is not requiring login - should check from POST?
   / Entityedit add test cases for unauthorized config requests (and more?)
   / From type display, want easy retreat to default display for collection
   / View_type display should suppress add-field option.  Similar for View_list and View_field?
   / suppress _initial_values as option when selecting type/view/list
   x Add field allows new view type to be created, but how to make this default for displayed type?
   / Generic field renderer for entityref as selection among available entity ids.  Use for field selection.  Options should be reworked using this form of enumeration, handled on the fly as required, using type information from the field definition.
   / Type view should have dropdowns for default view and list
   / List view selector syntax isn't working: need to nail down how type selection can work.  In saved data, I'm seeing '"annal:type": "annal:EntityData"', which isn't realy helpful.
       / change all references to annal:type to @type, in sitedata and code (i.e. URIs/CURIE values).  E.g. annal:Type, annal:View, annal:EntityData, etc.
       / for annal:type, assign local type_id value.  Consider renaming as annal:type_id.
       / annal:type is retained for URI/CURIE of entity class (is this helpful?)
       / list type selectors then use local type_id values.
   x @type list selector - allow selection by type substring - e.g. coll/type
   / When not logged in, should still have option to select a different view
   / From list view, continuation URI for new, copy, etc should exclude message parameters.  In particular, links in rendered fields have the extra stuff.  (But do include ?search param)
   / Customize > delete record > confirm : returns to wrong place
   / Generalized enumeration types
       / Define new RecordEnum class with type_id parameter on constructor; dynamically created directory paths; dynamic class creation?
       / Test cases for RecordEnum
       x Add optional type_id to all entity constructors (ignore on existing)
       / Update entitytypeinfo to support enum types
       / More test cases?
       / Review, rationalize type naming and type ids.  Update sitedata.
       / Update list type field definition
       / Update tests using list type field definition
       / Create type records for enumeration types, used for:
           - locating the default view and/or list id for records of that type
           - getting entity @type URI/CURIE values while editing
           - getting a view/edit link to type record
           - See notes in models.typeinfo
   / Enumeration type for list types (list/grid: default list)
       / Update field definition
       / Create type record
       / Update/add tests cases
   / Enumeration type for field render types (text, testarea, etc...); use in fields display
       / Create enumeration data
       / Update field definition
       / Create type records
       / Update/add tests cases
       / development test site is broken - why?  Isolate problem in test before fixing.
   / allow '//' comments in JSON files - strip out before parsing JSON (but leave blank lines)
   / Don't show Bib_* fields for non-biblio record types 
       x Move Bib_* fields to separate "built-in" collection
       x Can enumeration-like logic be used to support sub-areas in site data?
       * Long term is to move Bib_ field types out of site data, and provide easy way to incorporate library fragments into new collections, but for now they are part of the test environment.  See below.
       * Alternative might be value-scoped enumerations
       / Update EntityFinder logic to support tests comparing with enclosing view fields
       / Update entity selector call site (just one)
       / Update selector syntax and sitedata
       / Use EntityFinder logic in enumeration selection (FieldDescription.py)
       / Add view context to FieldDescription
       / Introduce biblio record type
       / Introduce biblio record list
       / Update test cases
       / Field name updates (field_render, value_type)
       / Update test cases
       / Add fields to restrict bib_* fields to BibEntry views
           x Declare additional/multiple types for entity?
       / Update field selector view
       / Use field selector in FieldDescription
       / Update test cases
9. Prepare for release 0.1
   / feature freeze
   / version identifier in system
   / remove dead code
   / test with Django 1.7
   / installation package
   / test installation on non-development system
       / sorting of enumeration lists
       / sorting of entity lists (by typeid then entityid)
       / sorting of entity lists enumerated in tests
       * There could be more test cases that need hardening, but so far all pass on a Linux deployment
   / check python version in setup
   / __init__.py in annalist_root dir causes test failure on Ubuntu 14.04; cf. https://code.djangoproject.com/ticket/22280.   Removing it solves the test case problem, but it was included originally to get the setup.py script to work as intended.  Try removing it and see if we can get kit builder to work.
   / Login page - link to local Django login & admin pages
   / Fix profile display with local credentials
   / Logged-in username should appear in top menu; e.g. xxxx profile or xxxx: profile logout
   / root URI - redirect to /annalist/site/
   / utility/script for running tests
   / utility/script for site creation
   / utility/script for running server
   / online help text (initial)
   x Test installation on Windows (De-prioritized for now. Tests pass, but having problems accessing the settings when running the server. Change directory?)
   - Documentation
       / release notes/introduction;  link from README (about this release); key missing features/issues
       / installation - link from README
       / getting started - reference installation then walk through demo sequence; link from README (getting started);
       > demo script (needs cleaning up)
       / using Annalist - flesh out; link from README
       / flesh out introduction/overview
       - how to setup OpenIDConnect providers - move to separate document; link from installation doc
       - tidy up README
       / Move remaining TODOs to Roadmap and issues
       - Flesh out roadmap
   / Create mailing list -- see https://groups.google.com/forum/#!forum/annalist-discuss
   > Demo deployment
   / Demo screencast -- see http://annalist.net
   - Final updates to master
   - Post kit download
   - Upload tom PyPI
   - Post announcement to Google Group, and elsewhere

