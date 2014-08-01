## Web application outline plan

Guided by mockups per https://github.com/gklyne/annalist/tree/develop/mockup

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
   - fix entity links to use default view URI (/d/...)
   - add_field button on entity edit displays
   - implement "add repeating field" option to view edit (and entity view?)
   - identifier display: try to find label instead of CURIE display; augment sitedata accordingly?
   - allow '//' comments in JSON files - strip out before parsing JSON (but leave blank lines)
   - align type ID values used in local URI construction with type URIs/CURIEs
   / tests
     / skipped '@@TODO defaultlist default-view button handler'
     / skipped '@@TODO defaultlist search button handler'
     / skipped '@@TODO genericlist default-view button handler'
     / skipped '@@TODO genericlist search button handler'
       / annalist.tests.test_entitygenericlist.EntityGenericListViewTest
     / skipped '@@TODO genericlist default list button'
       / annalist.tests.test_entitygenericlist.EntityGenericListViewTest
8. Extend form-generator
   / support repeated field group (to support RecordView and BibJSON)
   - support alternate displays for different subtypes (to support BibJSON)
9. Read-only entity data view
   - based on generic entity edit view, but using different render field options
   - update URI dispatching
   - include default view
10. Code improvement - lists
   - move invocation of authentication to the immediate response handler code?
   - refactor list description access out of context handling code (avoid multiple reads)
   - refactor code from entityeditbase into more specific views where possible
   - rename what is left of entityeditbase -> entityviewbase, or more to generic module
   - review URI for delete type/view/list confirmation
   - use proper indexing to accelerate search (maybe later?)
11. Code improvement - views
   - where possible, migrate methods from editentitybase to subclasses
   - review logic - ideally, form handlers will access data from form, then hand off for processing
   - review record view description form (create data and configure URIs)
   - review field description form (create data and configure URIs)
   - review record list description form (create data and configure URIs)
   / add "new field" logic to entity edit POST handler
12. Display enhancements
   - add type links to list view (link to typed list view...?)
       - (should use same base enhancements as entity links at step 5)
         - cf. [https://github.com/gklyne/annalist/commit/ff16e6063a2fee193e6e0080a77bfc738381a275]()
       - Update field in default list displays
   / list_view response handler (needs generic view to make sense; view button to redisplay)
13. Grid view
14. Generic entity selector (based on canned sparql expressions?)


## Tests required:

- Missing resource error reporting in:
  - annalist/views/collection.py
  - annalist/views/defaultedit.py
  - annalist/views/defaultlist.py
  - annalist/views/recordtype.py


## Misc TODO

- CSS style association with entity types, so (e.g.) different types can be colour-coded.
- entity list view: add javascript for selection classes (hide checkbox and highlight row when clicked)
- entity should carry URI only.  Other fields (host, path, etc. should be generated as required.  Suggest use an internal value that allows x.uri.path, .host, etc. as required)
- Convert literal CURIES to namespace references
- Review field descriptions in sitedata: type values seem to be inconsistent??? (e.g. Type vs Entity_type?).  May need to start some proper documentation of the form data descriptions.
- rationalize/simplify fields and methods in site/collection model classes - there appears to be some duplication
- review URI design: can we revert to original design (without /c/, /d/, etc.)?
- Login link to include option to redirect to failed page, with form fields populated (i.e. don't lose values entered)
- Complete authorization framework
- think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
- think about handling of identifier renaming (re-write data, record equivalence, or ...).  (See also "data storage" below.)
   - when renaming through edit form, update URI if it corresponds to previous ID??
   - need to think about maintaining a list of correspopnding URIs?
- Use server-internal revectoring?  What about delete multiple?
- currently there's some inconsistency about this: confirm views are rendered directly (as this allows form parameters to be provided directly), but other form action links are handled by redirection.  Try to be more consistent about this?  Create a more general pattern for handling continuation forms?    Note: redirect means that different view GET function signatures, with values provided in the request URI, are handled in generic fashion.  POST views are more easily handled directly with form parameters as supplied dictionary
- move util.py to utils package, and rename?
- look into using named tuples instead of dictionaries for rendering
  - cf. http://stackoverflow.com/questions/1336791/
- replayable log/journal of data editing actions performed (CW14)
/ view collections doesn't use entered label - problem with entry vocab? (Fixed)
/ move entity I/O logic in util module to entity module (keep it all together)
/ abstract definition of `field_context` - currently defined implicitly in `views.entityeditbase` (overtaken by redesign)
x can "Confirm" form continue to a DELETE operation?  Can forms reliably do this?  NO


## Future features (see also Misc above)

- Spreadhsheet bridge
- BLOB upload and storage
- Research Objects presentation
- Checklist integration
- use HTTP to access data; use standard web server backend
  - need to address auth, resource enumeration (WebDAV?), other issues
  - NOTE: need to address problem of getting HOST part of site URI when initializing a collection;
   can this logic be shifted to request code instead of __init__?
- more field types, including link browser
  - image grid + metadata pop-up for mobile browsing?
- alternative OIDC identity providers
- provenance data capture (e.g. - look at creating additional resource in entity._save)
- provenance pingbacks - distributed provenance for real data?
- git integration for data versioning
- dat integration for versioning? (https://github.com/maxogden/dat)
- Memento integration for old data recovery
- ResourceSync integration for data sync
- Shuffl integration?
- RML integration for data bridges

### Entity abstraction and storage

- replace direct file access with HTTP access
- Note that it should be possible to take an Annalist site directory and dump it onto any regular HTTP server to publish the raw data.  Web site should still be able to work with that.
- think about storage of identifier URIs (e.g. record type URIs.)  Should they default to be:
  (1) relative to self
  (2) relative to base of site
  (3) relative to host
  (4) absolute
  (5) relative to base of collection
  Currently, it's (3) or (4), but I think I favour (2).  The intent is that the URI field
  can be fixed by explicitly entering an absolute URI, but until then they are allocated
  per site.  The expectation is that if data are moved, it will be as complete collections
  to ensure they are accompanied by their associated metadata.

### AnnalistGenericView:

- Generic renderers, all driven by a supplied dictionary:
  - HTML
  - JSON-LD
  - uri-list
- but serve native format directly.

### Deployment:
- look into using Vagrant and/or Puppet/Chef/...

### Authorization

- Assume use of annalist form data under control of suitable authority
- Focus on form of authorization data
- Back-fit to form interface for creation of data; figure what seeding is needed


## Applications

* Cruising log
* Image database (bioimage revisited)


## Explorations

* Choose web server
  * probably Apache, considering nginx, but deferred until suitable OAuth2/OpenID-connect plugin is available
  * until then, using DJango for everything while ideas are fleshed out
* Authentication mechanism
  * Going with OAuth2/OpenID-Connect for now
  * Currently working with Google as IDP; loooking for alternatives
  * Considering OAuth2-Shibboleth bridge for uni deployment (have link somewhere in notes)
  * Oauth registration - note ongoing work in IETF
* Access control model
  * TBD; expect to use elements from UMA in due course
  * For now have very simple authorization function that requires authentication for up-dates, otherwise open.
* Define on-disk structure
    * Directories
    * Files
    * See https://github.com/gklyne/annalist/blob/develop/src/annalist_site/annalist/layout.py
    * @@NOTE: wean off direct directory access and use HTTP
* Define data access internal API details for web site
  * First cut in progress
  * @@NOTE: remember to use simple GET semantics where possible; may need to revisist and simplify
  * @@TODO: current implementation is file-based, but details are hidden in Entity classes.
* Define UI generation details
* Implement data access API details
  * Mostly straight HTTP GET, etc.  (Need to investigate access and event linkage - currently using direct file access for concept demonstrator.)


