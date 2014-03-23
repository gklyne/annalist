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
   - new entity from list-all display needs default type OR edit field has type selector, with logic to check type on save (treat type as part of id here)
   - add entity links to list view
   - list_view response handler (needs generic view to make sense; view button to redisplay)
   - default_view response handler (needs generic view to make sense)
   - search response handler (later; see below)
   / connect site display to default display of entities, not customize
   / connect list display to record view display
   / build entity selector logic into list view
6. Generic entity view and editing
8. Generic record list display and editing
7. Record view display and editing (data to drive generic view/list)
   - record view description form
   - field description form
   - record list description form
9. Read-only data view
?. Grid view
?. Generic entity selector (based on canned sparql expressions?)
?. implement search within list view

## Tests required:

- Missing resource error reporting in:
  - annalist/views/collection.py
  - annalist/views/defaultedit.py
  - annalist/views/defaultlist.py
  - annalist/views/recordtype.py


## Misc TODO

- entity list view: add javascript for selection classes (hide checkbox and highlight row when clicked)
- entity should carry URI only.  Other fields (host, path, etc. should be generated as required.  Suggest use an internal value that allows x.uri.path, .host, etc. as required)
- Convert literal CURIES to namespace references
- Review field descriptions in sitedata: type values seem to be inconsistent??? (e.g. Type vs Entity_type?).  May need to start some proper documentation of the form data descriptions.
- rationalize/simplify fields and methods in site/collection model classes - there appears to be some duplication
- review URI design: can we revert to original design (without /c/, /d/, etc.)?
- Login link to include option to redirect to failed page, with form fields populated
- Complete authorization framework
- think about use of CURIES in data (e.g. for types, fields, etc.)  Need to store prefix info with collection.  Think about base URI designation at the same time, as these both seem to involve JSON-LD contexts.
- think about handling of identifier renaming (re-write data, record equivalence, or ...).  (See also "data storage" below.)
   - when renaming through edit form, update URI if it corresponds to previous ID??
   - need to think about maintaining a list of correspopnding URIs?
- Use server-internal revectoring?  What about delete multiple?
- currently there's some inconsistency about this: confirm views are rendered directly (as this allows form parameters to be provided directly), but other form action links are handled by redirection.  Try to be more consistent about this?  Create a more general pattern for handling continuation forms?    Note: redirect means that different view GET function signatures, with values provided in the request URI, are handled in generic fashion.  POST views are more easily handled directly with form parameters as supplied dictionary
- move util.py to utils package, and rename?
- entity._save: think about capturing provenance metadata too
/ move entity I/O logic in util module to entity module (keep it all together)
? view collections doesn't use entered label - problem with entry vocab? (Fixed?)
- look into using named tuples instead of dictionaries for rendering
  - cf. http://stackoverflow.com/questions/1336791/
/ abstract definition of `field_context` - currently defined implicitly in `views.entityeditbase` (overtaken by redesign)
x can "Confirm" form continue to a DELETE operation?  Can forms reliably do this?  NO

## Future features (see also Misc above)

- try alternative OIDC providers
- spreadhsheet bridge
- Research Object presentation
- use HTTP to access data; use standard web server backend
  - need to address auth, resource enumeration (WebDAV?), other issues
  - NOTE: need to address problem of getting HOST part of site URI when initializing a collection;
   can this logic be shifted to request code instead of __init__?
- more field types, including link browser
  - image grid + metadata pop-up for mobile browsing?
- provenance data
- git integration for data versioning
- memento integration for old data recovery
- ResourceSync integration for data sync
- Shuffl integration?

### Entity abstraction and storage

- replace direct file access with HTTP access
- Note that it should be possible to take an Annalist site directory and dump it onto any regular HTTP server to publish the raw data.  Web site should still be able to work with that.
- think about storage of identifier URIs (e.g. record type URIs.)  Should they default to be:
  (1) relative to self
  (2) relative to base of site
  (3) relative to host
  (4) absolute
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


