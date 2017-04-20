# Annalist v0.1 release notes

Release 0.1 is the first public prototype of Annalist.  It contains what I hope is sufficient tested functionality for evaluation purposes, but there may be intended capabilities not yet fully implemented, and many refinements to be applied.

A summary of issues to be resolved for product release can be seen in the [issues list for the first alpha release milestone](https://github.com/gklyne/annalist/milestones/V0.x%20alpha).  See also the file [documents/TODO.md](https://github.com/gklyne/annalist/blob/develop/documents/TODO.md) on the "develop" branch.


## Current release: 0.1.37

This release contains candidate feature-complete functionality for an Annalist V1 software release.  The aim has beemn to complete features that are seen as likely to affect the stored data structures used by Annalist, to minimize future data migration requirements.  The intent is that this release will be used in actual projects to test if it offers minimal viable product functionality for its imntended use.  Meanwhile, planned developments will focus more on documentation, stability, security and performance concerns.

### Revised view definition interface

Extensive changes that aim to simplify the user interface for defining entity views (specifically, fields that contain repeating groups of values) by eliminating the use of separate field group entities.  This in turn has led to changes in the underlying view and field definition structures used by Annalist.

Also added are data migration capabilities for existing data collections that use record groups. These have been used to migrate installable collection data.

The `Annalist_schema` instalable collection data (which provides RDF-schema based definitions for the Annalist-specific vocabulary terms) has been updated to reflect the field group changes.

### Other features

- popup help for view fields (tooltip text) is defined seperately from for general help text in a field definition.  (HTML5 tooltips don't support rich text formatting, so thios was limiting what could be included in the field definition help descriptions.)

- the installable collection `Journal_defs` has been split into two, with the aim of improving ease of sharing common definitions:
    - `Resource_defs` provides field and view definitions for uploaded, imported and linked media resources (currently image and audio), and annoted references to arbitrary web resources.  It also provides a number of commionly used namespace definitions (dc, foaf, and a namespace for local names without global URIs).
    - `Journal_defs` (which uses media definitions imported from `Resource_defs`) now provides just the (mainly) narrative journal structure that has been found useful for capturing some kinds of activity description.

- An `annalist-manager` subcommand (`migrateallcollections`) has been aded to migrate data for all collections in a site.

### Bug fixes

- Editing an entity inherited from another collection (which is supposed to create a new copy of that entity in the current collection) was generating an error when saving the edted entity.  The fix to this involved extensive refactoring of the entity editing and save logic to keep better track of the collection from which the original entity data was obtained.

- Fixed site data and installable collection data so that entity selection for inclusion in fields presenting drop-down selection lists would operate more consistently.


## Status

The Annalist software is approaching the level of functionality that will be the basis for an initial full software release.  The primary goals of Annalist, which are substantially implemented, are:

* Easy data: out-of-box data acquisition, modification and organization of small data records.
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data, with links in and links out.

Key features implemented:

* Simple installation and setup procedure to quickly get a working installation
* Highly configurable form interface for entering, presenting and modifying data records, built using self-maintained configuration data.  The core presentation engine is substantially complete, but additional field renderers are still required to support a wider range of basic data types.
* Grid-based responsive layout engine (currently using Zurb Foundation)
* File based, versioning-friendly, textual data storage model;  data design is RDF-based, and uses JSON-LD elements, but contexts not yet defined so it's just JSON with RDF potential.
* Ability to create new entity record types, views and listing formats on-the-fly as data is being prepared
* Authentication with 3rd party IDP authentication (current implementation uses OAuth2/OpenID Connect, tested with Google, but should be usable with other OpenID Connect identity providers).  (Note access control is separate - see "Authorization" below.)
* Authorization framework for access control, applied mainly per-collection but with site-wide defaults.
* Support for linking to and annotating binary objects such as images.
* Image rendering
* Audio clip rendering (via HTML5 capabilities)
* Support for JSON-LD contexts.

Intended core features not yet fully implemented but which are under consideration for future releases:

* Full linked data support, recognizing a range of linked data formats and facilitating the creation of links in and out.  (Links can be created, but it's currently a mostly manual process.)
* Serve and access data through a standard HTTP server (current implementation uses direct file access).
* Grid view (e.g. for photo+metadata galleries).
* Data bridges to other data sources, in particular to allow Annalist to work with existing spreadhseet data.

See the [list of outstanding issues for initial release](https://github.com/gklyne/annalist/issues?q=is%3Aopen+is%3Aissue+milestone%3A%22V0.x+alpha%22) for more details on planned features still to be implemented.

There are many other features noted on the project roadmap that are not yet planned for inclusion as core features.  As far as possible, future development will be guided by actual requirements from applications that use the Annalist platform.


## Feedback

The main purpose of this release is to be a viable platform for getting feedback from potential users of the software.  In particular, I'd like to hear:

* If installation and getting a running service on a computer meeting the indicated prerequisites takes longer than 10 minutes.  What were the stumbling points?
* Any problems that occur whle trying to use the software.
* Ways in which the software does not meet preferred workflows for collecting data.
* Any must-have features for the software to be useful.
* Any other thoughts, ideas, or difficulties you care to report.

If you have a github account, feedback can be provided through the [github issue tracker](https://github.com/gklyne/annalist/issues).  Otherwise, by message to the [annalist-discuss forum](https://groups.google.com/forum/#!forum/annalist-discuss) at Google Groups.


## Development

Active development takes place on the [`develop` branch](https://github.com/gklyne/annalist/tree/develop) of the GitHub repository.  The `master` branch is intended for stable releases, and is not used for active development.  It would be appreciated if any pull requests submitted can against the `develop` branch.


# Further information

(Many of these documents are still work-in-progress)

* [Annalist overview](../introduction.md)
* [Installing and setting up Annalist](../installing-annalist.md)
* [Getting started with Annalist](../getting-started.md)
* [Guide to using Annalist](../using-annalist.adoc)
* [Simple demonstration sequence](../demo-script.md)
* [Frequently asked questions](../faq.md)
* [Developer information](../developer-info.md)
* [Development roadmap](../roadmap.md)


# History


# Version 0.1.37, towards 0.5.0

- [x] Absorb field groups into field defs
    - This is an extensive change that aims to simplify the user interface for defining certain types of field (specifically, those that contain repeating groups of values) by eliminating the use of separate field group entities.  This in turn has led to a significant change in the underlying view and field defiition structures used by Annalist.  Also added are data migration capabilities for existing data collections that use record groups, which have been used in turn to migrate installable collection data.
    - [x] Modify field definition reader to use locally defined fields rather than group reference
        - [x] in FieldDescritpion.py, use internal structure that is just a list of field id+property+placement from group def:
            - [x] Replace: group_view -> field_list
            - [x] Don't store group view in FieldDescription (store field list instead)
            - [x] Update group_view_fields to return list if present
            - [x] field_desc.has_field_group_ref needs rework to align with refactoring
            - [x] if list is defined within field definition, use that
            - [x] Rename: group_ids_seen -> field_ids_seen (recursion check)
    - [x] Extend field definition view to include list of fields
        - [x] Add field Field_fields to field view
        - [x] Define field Field_fields, using field definitions from group Group_field_group
        - [x] Copy fields Group_field_sel, Group_field_property, Group_field_placement and rename references in Field_fields
    - [x] Update site definitions to use field lists in field definitions
    - [x] Eliminate field group definitions from site data
    - [x] Modify or eliminate task buttons that create field group entities
    - [x] Check for other uses of field group reference field
        - [x] entityedit.py save_invoke_task (task dispatching)
        - [x] entitylist.py get_list_entityvaluemap
        - [x] test_sitedata.py check_type_fields
        - [x] test_render_repeatgroup.py
        - [x] Test Define repeat field button in deployed software
            - [x] Define repeat field - button text mentions group
            - [x] Define repeat field - value type should be annal:Field_list
            - [x] Referenced field view - entity type field should be blank, or field list
            - [x] Field entity type help text mentions group
            - [x] Define repeat field - confirmation message mentions group; message needs refinement
        - [x] fielddescription.py
    - [x] Check for and eliminate other uses of RecordGroup class
        - [x] test_render_ref_multifields.py
        - [x] views/form_utils/fielddescription.py
    - [x] Remove field group field from field view definition
    - [x] Update field view help text to mention subfields, not field group
    - [x] Seek out other references to field group type name or URI
        - NOTE: references to group type, views, lists remain for migration support, and free-standing view and list definitions, remain -- for now.
- [x] Migrate group references in user field definitions to use internal field list
    - [x] Add logic to RecordField to import field definitions from group definition
    - [x] Warning on migration if value type of repeat field does not match type of referenced group
    - [x] Add optional deprecation warning when recordgroup is instantiated (except for migration)
        - NOTE: EntityTypeInfo scans suppress these warnings, as they're used by migration logic
    - [x] Above changes should mean all live references are to inline field lists
    - [x] Add _group rename to collection migration function
- [x] Test migration functionality
    - [x] Add test case to test_data_migration
    - [x] Apply migrations to installable collections
        - [x] Install software then use annalist-manager commands to apply migrations;
        - [x] Check, and copy migrated data back to source tree
        - [x] Annalist_schema)
        - [x] Bibliography_defs
        - [x] Concept_defs
        - [x] Journal_defs
        - [x] RDF_schema_defs
    - [x] Eliminate group definitions in installable collections
- [x] Add annalist-manager option to migrate all collections in site
    - `annalist-manager migrateallcollections`
    - [x] Fix up installable collection problems picked up by collection migration 
- [x] BUG (attempt to save copy of site label field):
        - Steps to reproduce:
            - Select scope all listing of entities
            - Select site entity
            - Click "edit" button
            - Enter new entity id
            - Click Save
        - Problem appears to be that the software was trying to copy the original entity data (as part of a rename operation) from the current collection rather than the collection from which it has been inherited.
    - [x] Handle change of collection like change of type: copy data to new location
        - [x] GET: copy original collection id to form as 'orig_coll'
        - [x] POST:
            - [x] extract orig coll id from form, default to current coll id
            - [x] save collection id information into DisplayInfo object
        - [x] DisplayInfo.__init__: initialize collection id values
        - [x] DisplayInfo.set_type_entity_id: set collection id values
        - [x] entityedit references to orig_type_id; also check orig_coll_id
        - [x] Need to be able to retrieve original collection type info for copy
        - [x] Check original collection access is honoured
            - [x] fairly extensive changes to EntityEdit and DisplayInfo logic to keep track of the (possibly inherited) collection from which an entity is accessed.
            - [x] Exposed a conflict with _user entity access; for now have added a hack in DisplayInfo.check_authorization, and added a new TODO (below) to implement a more principled interface to allow per-entity access controls.   Also have paper notes for cleaning up access control checks.
            - [x] Add test case for attempt to view/copy/edit entity inherited from collection with no access
        - [x] New test case; edit inherited value with attachment
- [x] Fix handling of restriction expression for subfield selection.
    [x] Need test case coverage for subfields in field defintion, and domain and/or range classes in RDF_schema (e.g. _field/subpropertyOf on _field/subpropertyOf_r)
    [x] In FieldListValueMap, add {'group': field_desc_dict} to extra value context.
        - Should be accessible in restriction expression as 'group[...]'
    [x] Update field and view forms help text.
- [x] Annalist_schema add annal:field_fields property.
    - [x] Renamed type URI for field lists to match schema domain value.
- [x] annalist.namespace - default to CURIE, use .URI for URI.  Affects JSON-LD context test.
    - [x] Removed default option for now: everything is .URI or .CURIE
- [x] Provide field popup help (without MarkDown) separately from comment field
    - [x] Add new property URI to ANNAL namespace
        - annal:tooltip
    - [x] Add new field; change label on comment field
    - [x] Use annal:tooltip in preference to rdfs:comment when rendering field.
        - handled in render_fieldvalue.py via field.field_tooltip ...
        - ... calls bound_field.get_field_tooltip()
        - ... uses self._field_description['field_help']
    - [x] Default to rdfs:comment value if blank
    - [x] Re-order fields in field view so tooltip comes toward end
    - [x] Add migration logic to copy comment to tooltip and add heading for comment:
        - "# (label)\r\n\r\n(Tooltip)
        - test case in test_data_migration.py
        - adjust test logic to accommodfate this migration
    - [x] Edit sitedata field definitions
- [x] Split installable collection Resource_defs from Journal_defs
- [x] Update installed software on fast-project.analist.net
- [x] Update data migration logic tp fix entities whose 'annal:type' value does not match the corresponding type definition (which could occur when migrating old data).


## Version 0.1.36

This is mainly a "maintence" release, with changes to support and management tooling and a new installable data collection.  There are relatively few changes to the core software.

Changes include:

* Server logging and log access enhancements.  Among other things, these make it possible for Annalist users withj site ADMIN permissions to view server logs without a shell login on the server host system.
* Additional command line tools for setting up initial user accounts.
* Improved control over default access permissions for a collection.
* Small internal changes and improvements to data migration logic.
* Improved reporting of some incorrectly defined view fields.
* New installable collection data (Concept_defs) with definitions for associating SKOS Concept tags with entities.


# Version 0.1.35, towards 0.1.36

- [x] Access to page link without continuation (view only)
    - Added permalink to entity view page, after page heading
- [x] Rearranged page layout so that page heading comes below top nav bar
- [x] Logging enhancements:
    - [x] link to view log in bottom bar, if admin permissions
    - [x] log file rotation (max 2Mb) for "personal" config
        - could easily be extended to other configurations
- [x] Log rotation at server startup
    - web interface link shows entries for the current server run
- [x] annalist-manager options for users:
    - [x] annalist-manager createlocaluser [ username [ email [ firstname [ lastname ] ] ] ]
        - This provides a way to create local (Django) user accounts from command line
    - [x] annalist-manager setuserpermissions [ username [ permissions ] ]
        - this allows site-level permissions to be set for an identified user
- [x] internal renaming `annal:Slug` type URI to 'annal:EntityRef'.
    - [x] reflects updated structure of internal entity references
    - [x] renamed in code and site data
    - [x] migration logic added
- [x] revise authorization logic to include default-user permissions for collection
    - permissions  associzted with the default user ID in a collection are applied when accessing that collection.  Provides a way to configure per-collection default access rules.
- [x] Migration logic: check that new supertypes are applied
    - [x] Add Collection.update_entity_types
    - [x] Call Collection.update_entity_types from CollectionData.migrate_coll_data
    - [x] Add test case (in a new test suite for data migration tests)
- [x] Improved error handling when a field uses an enumerated value render type without specifying a references type.  This was causing server errors; now it provides a somewhat more helpful user error message.
- [x] Add new installable collection (Concept_defs) for defining and associating SKOS Concept tag fields.
    - [x] define type
    - [x] define view
    - [x] define list
    - [x] define related concepts fields and group
    - [x] define broader concepts fields and group
    - [x] define entity concepts field for associating concepts with an entity
- [x] annalist.net front page - link to CEUR paper on web


## Version 0.1.34

This is a summary of the main changes.  For more detailed information, see the changelist below for version 0.1.33.

### Data layout changes

The layout of collection data has been revised so that the file system layout more closely matches the URL structure for accessing collection content.  The directory `_annalist_collection` that was previously used for collection configuration data such as type and view definitions is no longer used, and all data is in directory /d/ under the collection root directory.  Type names for internal data (e.g. `_type`, `_view`) now all start with '_' to avoid clashes with user-defined types.  Enumerated values are now treated as additional built-in types, rather than the special cases used previously.

The effect of this is to make access and links to data records work consistently when using either `file:` or `http:` URLs.  It also means that the JSON-LD context file does not need to be duplicated within a collection.

Logic has been added to the Annalist server to automatically migrate older collections to the new layout when accessed.

Some inconsistencies between built-in site data and installable collection data (that were causing warnings when generating context data) have been corrected.  In particular, the repeating "See also" field in collection `Journal_defs` was inconsistent with the similar site-defined field in default Entity views.

The SQLite database file used for Django configuration and administration (and any locally defined user accounts) has been moved to the site root directory.  This prevents overwriting previous configuration options (and the site admin account) when site data is updated.

### Installable collection data changes

In the wake of data migration support and changes to the on-disk layout of data files, installation-supplied data collections have been revised.  Bibliography data definitions (used for some testing) have beenmoved out of the core Annalist site data and are now provided as an installable collection.

### Bug fixes and enhancements

Numerous bugs from the previous release have been fixed

* User with just CONFIG access to a collection can now edit collection metadata
* Collection, type and entity ids can now be up to 128 characters (was 32 characters)
* Installation of login button images
* Create login provider directory if needed when installing/updating site data
* In `Markdown` view fields, `$SITE` and `$COLL` symbol substitutions do not include host value (like `$BASE`)
* Add default view and list definitions to site data for enumerated values
* `annalist-manager installcoll` now has a `--force` option for installation over existing collection data.
* `annalist-manager createsite` now populates login provider configuration data
* `annalist-manager createsite --force` warns about loss of old user permissions
* "KeyError: 'recent_userid'" error report when no previous login is available
* `annalist-manager installcoll Journal_defs` fixed error in data

### Documentation improvements

* README.md front page and PyPI front page include pointer to annalist.net
* Data migration code uses proper reporting/diagnostic mechanisms
* Various enhancements to the built-in help text, with improved cross-linking between related pages.  Corrected several omissions.

## Version 0.1.33, towards 0.1.34

- [x] BUG: login button images not copied to new installation.
    - [x] Added identity_providers/images as static directory
    - [x] Remove login image from Annalist static data directory
- [x] BUG: when initializing/updating site data, create providers directory if needed
    - [x] Added 'ensure_dir' call to logic that copies provider details
- [x] BUG: Site users removed by software update ...
    - not 'updatesite', 'initialize', 
    - normal upgrade options don't see to do it: maybe use of `createsite --force`?
    - added further comment to createsite --force message
- [x] BUG: `annalist-manager createsite` does not populate provider data
    - works in 0.1.33
- [x] BUG: KeyError: 'recent_userid' when no previous login:
        ERROR 2016-07-04 09:12:44,921 Internal Server Error: /annalist/login_post/
      FIXED: check in new installation
- [x] BUG: `annalist-manager installcoll Journal_defs`
      FIXED: (syntax error in field data)
- [x] README front page and PyPI front page include pointer to annalist.net
- [x] Replace print statements in data migration code with a proper reporting/diagnostic mechanism.
- [x] BUG: user with CONFIG access is unable to edit the collection metadata.
      For view/edit collection metadata, need permissions to come from the referenced collection, not _annalist_site
- [x] Review length restriction on entity/type ids: does it serve any purpose?
    - Increased max segment length to 128 in urls.py and util.py function valid_id.

- [x] Review file/URL layout for enums, and more 
    - use /d/ for all types, including built-ins
    - note extra logic in models.collectiondata and models.entitytypeinfo, etc.
    - this reduces duplication of JSON-LD context files.
    - migration strategy
        - On opening collection, move collection directory content to /d/ directory.
        - On opening collection, rename any old enumeration types.
        - On accessing field definitions, convert any enumeration type references.
    - [x] avoid explicit reference to `_annalist_collection`
    - [x] collections and repeated properties:
        - Use `@id`, thus: { "@id": <some_resource> } .
        - This avoids creation of intermediate blank nodes in the RDF.
- [x] Re-work handling of built-in enumeration types
    - Reference as (<type_id>/<entity_id>: e.g. d/Enum_value_mode/Value_direct/)
    - also rename enum types; e.g. "_enum_value_mode".
    - [x] update site layout definitions
    - [x] rename site data files (for enum type and value definitions)
    - [x] update code and tests to work with new enumeration type names
    - [x] replace all references to old enumeration type names; fix
        - (note annal: namespace URIs use original names, without leading '_')
        - [x] Enum_field_placement
        - [x] Enum_list_type
        - [x] Enum_render_type
        - [x] Enum_value_mode
        - [x] Enum_value_type
    - [x] revise "Bib data type"
        - [x] make regular type
        - [x] remove special case logic in entitytypeinfo
        - [x] Need manual test of BibliographyData.
        - [x] Abandon old BibliographyData on demo system.
    - [x] update built-in help text
        - [x] update various references found in help text
        - [x] check refaudio, refimage links (using $COLL to access lists)
        - [x] check Annalist_schema
            - [x] Property/field_render_type (major edits)
            - [x] Property/field_value_mode
            - [x] Property/repeat_label_add
            - [x] Property/repeat_label_delete
    - [x] rename "field_type" -> "render_type"
        - note 'field_type' is also used in field descriptions for internal distinctions.
- [x] eliminate '_annalist_collection' subdirectory
    - just use collection /d/ for coll_meta.jsonld: extension will ensure no clash with type subdirectories
    - using /d/ for all data, including collection metadata, helps to ensure that relative references can work with http:// and file:// URLs (or access via Annalist and direct access to data).  Essentially, /d/ is the base URL for all collection data references.  But site data references won't work this way, so there is a distinction here between collection data and collection config metadata.
    - [x] update layout definitions
    - [x] generate JSONLD context in /d/ only
    - [x] new site migration
        - [x] move content of _annalist_site/_annalist_collection/ to _annalist_site/d/
            - handled by collection migration of "_analist site"
            - check site data update logic - am_createsite.updatesite
            - most site data is fully recreated on each update, via:
                - am_createsite.am_updatesite
                - Site.create_site_metadata
                - etc.
            - user and vocab entries are copied from previuous site data
        - [x] added logic to rename old site data to be clear it's no longer used
    - [x] collection migration
        - [x] move content of /_annalist_collection/ to /d/
            - this now done on collection load so that config is in right place for data migration
        - [x] rename old enumeration types
        - [x] regenerate context
            - done in collectiondata.migrate_coll_data
- [x] --force option for `annalist-manager installcoll`
- [x] See_also_r field duplicated in field options list?
    - [x] check errors in context file
        - Fix so far is to ensure Journal_defs uses property "@id" in group, as does Entity def
- [x] $SITE, $COLL symbols should not include host value (like $BASE)
    - Values set up in views.displayinfo.context_data
- [x] Problems with logic to archive old site data (am_createsite and maybe elsewhere)
    - [x] update setting to move sqlite database to root of site
    - [x] Migration logic in site update to move sqlite database 'db.sqlite3' to site root
    - [x] Also migrate old `site_meta.jsonld' in root of site (see am_createsite.py:163)
    - [x] Then rename old '_annalist_site/' directory - eventually, these archived directories can be removed.
- [x] Data migration: enumeration labels not available (e.g. for render types, list types)
    - [x] cf. http://localhost:8000/annalist/c/Performances/d/_field/Place/
    - [x] cf. http://localhost:8000/annalist/c/Performances/d/_list/Default_list/
    - Affected types: _field, _list, 
    - Enum type fields migrated:
        - [x] list_type (_list; recordlist.py)
        - [x] render_type, value_mode, NOT value_type (_field; recordfield.py)
- [x] Add view and list definitions for enumerated values to site data (cf. Enum_bib_type, type annal:Enum)
    - [x] View is basically default display plus URI
    - [x] List is like default list all (with types), but select for type URI annal:Enum
    - Note: have just defined one list for all enumerated values
        - a next step would be to define lists for per-enumeration values.


## Version 0.1.32

This release provides enhancements and bug fixes in a number of areas, as well as some major internal structural changes to the software.  Enhancements include:

* Re-working of the login screens to make the login process easier
* Improve JSON-LD context and data generation, in partcilar maming use of `@base` declarations so that internal entity references are interpreted correctly as relative URI references.
* Internal changes to collection data layout and details, and support for migration of existing collections.
* List definition view: provide button to display the defined list content
* List display: re-organize entity type and scope selection controls.
* Markdown and help text enhancements: provide variable substitutions for host, site, collection and base URLs so that help text can contain links that work independently of site location.
* "Customize" display - use help text from collection configuration file.
* New annalist-manager command to display location of site settings directory.
* Fix bug where collecton-defined data were not inherited from a parent collection.
* Fix form layout anomalies that were causing some fields to appear in unexpected locations.
* Fix bug in display of site-defined entity lists (defined in `_annalist_site`).

**NOTE**:  see section "Data structure changes and migration" below for information about migrating data collections to use the new format introduced in this release.

### Login enhancements

The login process has been enhanced in a number of ways:

* Local login (using the Django user database) is handled as just another provider.
* Per-provider login buttons are presented, rather than a drop-down list.
* A previously used user-id is presented as a default value.
* If no user-id is provided, a suitable value is constructed from the authenticated email address.  (In rare cases, this may conflict with an existing value, in which case an alternative Id must be specified.)
* On completion of the login process (and clicking "Continue" on the displayed user profile), the browser returns to the page from which the login sequence was initiated.  Similarly, on logout, the originally displayed page is re-displayed (permissions permitting).
* On successful completion of a login for a user that has not previously been seen by the system, a new user permissions record is created with the specified user id, authenticated email address and default permissions for logged-in users.  Another user with ADMIN permissions can assign appropriate permissions to this record, which is easier than creating a new user permissions record from scratch.

**NOTE**: On logging out, you may see an error report to the effect that permissions are required: this is not an error, but can be confusing.  It can occur after logging out while displaying a restricted-access page.  The error occurs when attempting to redisplay the same page, but now without appropriate access permissions.  There are plans to adjust this behaviour in a future release.

Internally, the login code has been refactored to make it easier to support alternative authentication mechanisms.


### Data structure changes and migration

The internal structure of a data collection has been modified.  Thje main change is that the directory names used for built-in data types (e.g. `_type`, `_view`, `_list`, etc.) have been changed to match the type id.  This is a first step towards making the structure of URLs and filenames more consistently, which in turn should reduce the incompatibilities between accessing data via annalist and accessing it directly.

A number of smaller changes have been made to Annalist-defined data records, particularly field definitions.  Existin g records are upodated to the new structure when they are read and saved, or when the data collection is migrated using migration options (2) or (3) described below.

Old collection structures are migrated automatically when they are accessed through Annalist (but see the note below about migrating inherited collections).

**NOTE**:  when migrating data collections for use with this release, ensure that inherited collections are migrated first.  Before migrating a collection, it is advasable to create a backup copy (e.g. with git).  Once migrated, data is no longer compatible with previous versions of Annalist.  Migrations can be performed in one of the following ways:

1. Viewing a collection from the Annalist site front page: this updates the collection data structure, but does not immediately update the individual data records.
2. Go to the "customize" view for a collection and click on the `Migrate data` button.
3. Using `annalist-manager migratecollection (collection)` - updates the collection data structure and also migrates data record contents.

The data migration faclities remain a work-in-progress, and should improve over future releases as we gain more experience using them.


### JSON-LD enhancements

With the release of [rdflib-jsonld v0.4.0](https://github.com/RDFLib/rdflib-jsonld/tree/0.4.0), the Annalist JSON-LD generation has been enhanced to make use of `@base` directives.  A consequence of this is that internal entity references, that were previously exported as literals, can be used as relative URI references, and appear as URI nodes when read as JSON-LD into an RDF graph.  Also, entity `@id` values are now exproted as `type-id/entity-id` valuyes that resolve against the declared `@base` URI to the correct entity URL.

For this to work as intended, collection entity data has to be migrated to the new format using the `@base` URI declaration.  See the above for details about about data migration.


### List selection and display

The options for displaying lists have been re-worked.  The following options affect the display of a list of entities:

* the list definition selected, which may constrain the entities that are selected for display,
* the type of entity selected for display, which sometimes conflict with a restruction in the list definition, and
* the scope of entities selected for display, which can be limited to the current collection, or may include all collections from which definitions are inherited.

The list definition used is specified in the list URL (using a path of the form `.../l/(list-id)/...`), or by the default collection display.

The type of entity selected for display may be specified in the list URL used (e.g. using a pathy of the form `.../l/(list-id)/(type-id)/`, or `.../d/(type-id)/`).  The displayed list may be empty if the type specified inthe URL does not match any type restruction specified by the list definition used.  If this happens, try clicking on the button labeled "List" (as opposed to the one labeled "List '(type-id)'").

Finally, the scope of a list display is selected by the checkbox labeled "Scope all".  By default, only entities from the current collection are displayed.  To see entities from inherited collecions too, select the checkbox and click again on the "List" (or "List '(type-id)'") button.  (As with previous releases, the menu bar can be used to select display of a list of entities of a specified type, or using a specified list definition.)

Also, a bug has been fixed that meant a search term inside a repeated field would not be discovered, so using the search field should now yield more useful results.


### Markdown and help text

When using Markdown fields in type, view, list, and field definitions to document a data collection, it is often useful to include internal links.  Previously, this had to be done with full path names, as relative references did not always work reliably.

This release adds symbol substitutions in markdown text for `$HOST`, `$SITE`, `$COLL` and `$BASE` which makes it easier to write internal links.  The variables are substituted before markdown formatting is applied.

For example, `[View]($BASE:_type/_view)` can be used in Markdown text to create a link to the type definition record for view definitions.

The online help text for the Analist internal definitions has been updated to use these symbol substitutions for internal cross-linking.


### Management, internals and bug-fixes

New annalist-manager commands have been added:

    annalist-manager sitedirectory [ CONFIG ]
    annalist-manager settingsmodule [ CONFIG ]
    annalist-manager settingsdir [ CONFIG ]
    annalist-manager settingsfile [ CONFIG ]

These commends respond with information about an Annalist configuration, and are implememnted in a way that can be used easily as part of a management script, if required.

The list view now includes a button that can be used to display the defined list.

The collection customization display now has a button that can be used to invoke migration of collection data: this duplicates the capability of the `annalist-manager migratecollection` command, and can be used without having terminal access to the Annalist host system.

Fix bug where collecton-defined data were not inherited from a parent collection.  This required making some changes to the alternative parent search logic in the entity models, especially the model used for record type data (the parent entity for all user-defined type entities).

Fix form layout anomalies that were causing some fields to appear in unexpected locations.  This has required a re-working of the field layout logic to explicitly wrap rows of fields.  The internal changes for this are quite extensive, and there are many test suite changes also required.

Fix bug in display of site-defined entity lists (defined in `_annalist_site`).

Fix bug in search function in list displays which meant that fields in repeated groups were not being searched, hence 
the results returned were missing some values that were expected to be included.


## Version 0.1.31, towards 0.1.32

- [x] annalist-manager config directory - display directory where config setting files are located
    - e.g. anenv/lib/python2.7/site-packages/annalist_root/annalist_site/settings/
    - (same as SITE_CONFIG_DIR in log)
- [x] Entity types list (and List list?) - provide link field to display list
- [x] Entity lists - set state of scope all checkbox to reflect scope parameter
- [x] Help text for 'Customize' display
    - This is now taken from the collection metadata, and may be edited there.
- [x] Fix behaviour of collection inheritance - data not inherited?
    - Modified logic that searches for alternative parents for user-defined data types.
    - Note that the search logic has reduced test suite performance by 10-15%.
    - May want to look later for optimizations here (e.g. cache collection data).
- [x] Establish collection as base URI for Markdown text links, or provide some kind of prefix expansion.
    - relative references are unreliable 
    - views/displayinfo.py, context_data is key function for assembling context info
    - substitution syntax:  $name, $name:, $[CURIE], $$ -> $, else as-is
    - Name characters are ALPHA, DIGIT, "_"
    - CURIE characters for subsitution: name characters, plus:
      "@", ".", "~", "-", "+", "*", "=", ":", ";", ",", "/", "?", "#", "!"
    - [x] add site_base_url (SITE), coll_base_url (COLL) and site_host_name (HOST) to context
    - [x] add BASE to context: path for relative reference of collection entities (includes `/d/`).
    - [x] define substitution function in displayinfo
    - [x] apply substitutions when setting help_markdown (displayinfo.context_data())
    - [x] apply substitutions in views/fields/render_text_markdown.py text_markdown_view_renderer.render
    - [x] test case (markdown renderer)
    - [x] documentation (markdown field render type)
    - [x] use substitutions in help text
    - [x] add link to markdown field render type in help fields using Markdown
    - [x] User view description field - add "markdown" text.
    - [x] Use $BASE substitutions in help text for installable collections
- [x] Rethink field padding model
    - Generate columns explicitly within rows, not assuming they will just flow.
    - All field lists are processed through FieldListValueMap
    - Each field is handled by a referenced FieldValueMap instance
    - [x] Define new class FieldRowValueMap
    - [x] Define renderer for field row that wraps list of fields as a row
    - [x] Re-work FieldListValueMap to break fields into rows and call FieldRowValueMap with each such group
    - [x] Check and fix test cases
- [x] Login window: implement "Local" as a provider, authenticated against the local Django user base.
    - [x] Gereralize default provider mechanism, make "Google" default provider
    - [x] Local login: use userid from login front page, if defined
    - [x] Local login redirects to login form - should display profile
    - [x] Retain userid on login front page after login failure
    - [x] Use buttons on login form instead of dropdown
    - [x] Profile display accept POST and redirect to continuation
    - [x] Save recent user id in session to facilitate login
    - [x] Allow blank user id and construct value from authenticated email
    - [x] Use button label from provider details (else provider name)
    - [x] Login/Logout/profile buttons to include continuation
    - [x] Login form cancel button: return to continuation URL
    - [x] Login messages to separate module for ease of translation
    - [x] Fix tests
- [x] Make login screen clearer
    - [x] if id is left blank, use email local part (with substitutions)
- [x] Rationalize login provider details handling
    - [x] Obtain scope from provider details file
    - [x] Save entire provider detail in request.session - access values from there
- [x] Login/logout: support continuation URI
- [x] New logins: automatically create new user record with default permissions.
    - This should make it easier to assign permissions
- [x] annalist-manager site data initialization: 
    - copy local id provider and examples to site config
- [x] Fix bug in display of entity lists from `_annalist_site` collection
- [x] Check out context definition conflict for list (cf. rdfs:seeAlso)
    - [x] Add test case for vocabulary view
    - [x] Add logic to generate set context for seeAlso
    - [x] Update all existing site data references to "RepeatGroup" and "RepeatGroupRow"
    - [x] Update site data and tests to use type-qualified render type and value mode values.
    - [x] Add migration logic for field definitions to use new render type names.
- [x] Changed "field value type" in field description for repeat/multifield reference fields to indicate
    the type of the referenced group, or if it contains a singleton the referenced target value type.
    These changes affect data rather than fundamental workings of Annalist; the tasks for creating
    repeat fields and multifield references have been updated.
- [x] Refactor context checking for field lists (`test_entitygenericlist`, `test_entityinheritlist`)
- [x] Migration options for references to `Field_render` and `Field_type` in views, groups and lists
- [x] Use "@base" declaration in entities
    - [x] Each entity/record type to declare a reference to base container URI
    - [x] Context file in base container
    - [x] Replace `_contextref` with `_baseref`
    - [x] For RecordEnum, use different reference to base directory so '_annalist_collection/' or 'd/' is accessed as context directory.  
    - [x] Don't generate enums/coll_context.lsonld.  Update context references in Enum values.
    - [x] Add base declaration to entity files, etc.
    - [x] Generate entity IDs relative to collection base directory
        - There's still some ad-hocery around handling of references to enumerated values.
        - See actions below to review URI and directrory usage.
    - NOTES:
        - `@base` ignored if used in external contexts;
        - `@base` can specified value be relative? YES:
            - [syntax sect 8.7](http://www.w3.org/TR/json-ld/#context-definitions) and 
            - [API sect 6.1](http://www.w3.org/TR/json-ld-api/#context-processing-algorithm) para 3.4
        - BUT: rdflib-jsonld implementation currently ignores `@base` when accessing an external context resource.
        - Use `(site_base)/c/(coll_id)/d/` as base URI so that entity ids (`type_id/entity_id`) work directly as relative references.  
        - Also `type_id` to retreive a list of entities of that type.
        - Thus use `{ "@base": "../..", @context": "@context", ... }` in entity data.
        - previously, there was a problem with rdflib-jsonld base URI handling.
            - cf. https://github.com/RDFLib/rdflib-jsonld/issues/33
- [x] BUG: JSON URI wrong in JSON-LD output? e.g. 
    "http://fast-project.annalist.net/annalist/c/Performances/d/Ensemble/Phil_Langran_band/Musician/Phil_Langran"
    shoud be: "http://fast-project.annalist.net/annalist/c/Performances/d/Musician/Phil_Langran/
    - [x] Change entity references (select rendered) to @type @id in context
        - cf. models.collection.get_coll_jsonld_context, etc.
    - [x] Rename directories used for built-in types to match type name
        - views.collection -> annalist.models.collectiondata.migrate_coll_data
        - am_managecollections -> annalist.models.collectiondata.migrate_coll_data
        - collection object is parameter
        - [x] Add new, old directory names to layout.py
        - [x] Find all references to directory names, use layout symbols
        - [x] Add function in collectiondata to rename directories
        - [x] Add call to directory migration function in collection view method from site
        - [x] Add call to directory migration function in collectiondata.migrate_coll_data
        - [x] Rename directories in sitedata in source tree and layout.
- [x] Fix bug in list search function: not finding values in repeated groups


## Version 0.1.30

This release provides improvements to data evolution, collection management, user interface changes aimed at facilitating collection navigation, and bug fixes.  It also advances the support for modular collections in `annalist_manager`, and provides some installable collection definitions.

### Data evolution support

Data evolution support has been enhanced by the inclusion of support in `annalist-manager`.  The idea is that data evolution can be substantially handled by:

a. Adding new Annalist types and fields.  This does not create any incompatibility with older data, so no migration of existing data is required.
b. Changing type URIs:  these will be updated in the normal course of using Annalist to manage the data.  References in views, fields and lists may need updating, or if previous type URIs are declared as supertypes of the new URIs then the old URIs used here can still be recognized.
c. Changing property URIs:  this will cause previously used URIs to not be recognized, unless the old URIs are declared as aliases for the new ones (in the appropriate type definitions).

The plan is that, when evolving a collection, a new collection can be created that inherits from the original, and changes can be made in the new collection.  When the desired changes present as desired, a migration report can be run to highlight where existing classes (types) and properties (views and fields) are changed, and suggest changes to supertype declarations and property aliases that can facilitate migration of data.  The report is an early experimental feature, and it is intended that it be enhanced with growing experience of actual migration requirements.

The new features added to `annalist-manager` are intended to facilitate use of collection modules in support of separation and sharing of definitions:

* `migrationreport old_coll_id new_coll_id` - produce a migration report of changes from `old_coll_id` to `new_coll_id`
* `annalist-manager migratecollection coll_id` - apply type and property changes to all entities in a collection.  Type URIs and property aliases are re-written for all entities in the collection by reading and re-saving each one.

### Data collection management support

Data collection management features added are:

* `annalist-manager copycollection` - makes a complete copy of collection definitions and data content.
* `annalist-manager installcollection` - installs a predefined collection from the software distribution into the an Annalist site.  The available collections ids are displayed if none is supplied.

New data collections have been created:

* `RDF_schema_defs` - provides Annalist definitions for Class, Datatype and Property that can be used to define RDF schemas as Annalist collections.
* `Annalist_schema` - uses `RDF_schema_defs` definitions to define an RDF schema for the Annalist namespace.
* `Journal_defs` - defines fields for a generic data collection based around journal entries with attached media.  The types and fields defined for media attachment have been arranged to allow linked, imported and uploaded media to be mixed in a list.  In our work, we have found these useful in a number of data collection projects where we start with very loosely structured data, around which more structured information is later crystallized.

### Site navigation changes

* The list display selection buttons are reorganized.  To list inherited definitions, the "scope" checkbox should be selected before clicking one of the **List** or **List <type>** buttons.
* Add a **Customize** button to entity edit form (enabled if CONFIG permission is available).
* Add a **Collection metadata** button to the Customize view, to facilitate access to collection metadarta editing.
* Add a **Migrate data** button to the Customize view to trigger data migration from the Annalist web interface (as an alternative to using `annalist-manager migratecollection`).

### Other changes

* Entity view displays no longer show ttoltips for the various fields, as they were not very helpful and sometimes confusing.  (Tooltips are still displayed in edit mode.)
* The (get the) *Data* button en entity view displays returns the underlying data with content type `tex/plain`, so that it displays immediately in the browser.  The `JSON-LD` link still returns the data as `application/ld+json`.
* When copying an enttity, the generated default entity Id incorporates the original entity Id.
* Various internal changes noted below in the version 0.1.29 change log.


## Version 0.1.29, towards 0.1.30

- [x] Add data migration logic for vocabs
- [x] Review how data migration can be handled. For now, using supertypes and property aliases.
    - [x] `annalist-manager `
    - [x] `annalist-manager migratecollection`
        - load and save every entity in a collection and rewrite context data.  
- [x] annalist-manager options to install/copy collection data
    - [x] `annalist-manager copycollection from to` (copy existing)
    - [x] `annalist-manager installcollection name` (predefined)
- [x] When supertypes are changed, need to regenerate @type fields of instances?
    - [x] refactor methods used for initialization, copy and migration
    - [x] add migration option on customize page
- [x] Add "Customize" button on entity edit and view pages, enabled with config permissions
- [x] Add "Collection metadata" button to collection edit (Customize) view.
- [x] Add "Migrate data" button to the collection edit (Customize) view.
- [x] List view: reorganize scope/type selection: 
    - [x] use "List <type>" and "List" buttons, with checkbox for "Scope all".
    - [x] Suppress "List <type>" if no type id is defined by the URI.
- [x] Drop tooltips from fields in view-only mode (they weren't very helpful).
- [x] Retrieve underlying JSON-LD data as text/plain or text/json for viewing in browser
- [x] Site vocabulary changes
    - [x] `Entity_see_also_repeat` -> `Entity_see_also_r`
    - [x] `Entity_see_also_repeat_field` -> `Entity_see_also_group`
    - [x] `owl:sameAs` -> `@id` (in `_group/Entity_see_also_r` - used by vocabs)
    - NOTE: only references found are in site data, so should be superseded by software update.
    - Check when software updates are applied to various deployments
- [x] When copying entity, generate new ID using id of opriginal entity
    - (entity.allocate_new_id, called by displayinfo.get_entity_info, called by entityedit.view_setup)
- [x] Remove all references to `field_target_type` - where needed, use `field_value_type` instead.
    - [x] Add migration entry in models.recordfield
- [x] Canonicalize JSON generation (sort keys) to minimize arbitrary version differences
- [x] Create schema definitions in Annalist for ANNAL namespace, as predefined collection data.
    - [x] When creating repeat field for field, display the created field.
    - [x] Create definitions for schema entities: classes and properties
    - [x] Create records for classes
    - [x] Create records for properties
    - [x] Separate collection into `RDF_schema_defs` and `Annalist_schema`
    - [x] Add `RDF_schema_defs` and `Annalist_schema` as predefined collection data
        - NOTE: current limitations of Annalist mean that the exported JSON-LD for RDF schema does not directly use standard RDF terms for everything.  For example, subclasses are referenced using a local URI reference rather than the global absolute URI, which can be obtained by defererencing the given reference and extracting the `annal:uri` value from there.
- [x] Refactor and review label/comment creation for entities generated by task buttons.
- [x] Add journal and note entry definitions (with image and audio resource fields) as installable collection.
- [x] Check layout/field alignment, adjust CSS: check with tutorial data (photo example)
- [x] Refactored handling of field rendering dispatch
    - hand off to individual render modules
    - rename `render_utils` module to `find_renderers`
    - eliminate special case logic in find_renderers module.
- [x] Provide overview description and resource links at annalist.net.


## Version 0.1.28

This release contains substantial cosmetic updates, and some bug fixes.

The main visible change is in the use of view, list and field comment text to provide online hekp and tooltips when editing or viewing data.  This provide some key documentation of user operation details in the user interface itself, rather than in separate documentation files.  External documentation is still needed for overview and HOWTO type information, but the aim is that it will not be so critical for finding details - especially in the area of view and field definitions and use.  These changes also mean that Annalist collections can contain domain-specific online help for their specific purposes and definitions provided.

New functionality in this release is the possibility to use common fields for uploaded, imported and linked resources (e.g. images and audio clips).  This is achieved by creating supertypes that subsume the various sources, which can then be referenced and displayed.  An example of this is the FAST project "Performances" collection description of the [Phil Langran Band](http://fast-project.annalist.net/annalist/c/Performances/d/Ensemble/Phil_Langran_band/), which presents an image linked from the band's web site, and another that has been uploadsed to Annalist.  This capability was previously unavailable due to bugs in the form presentation logic, which have been fixed inthis release.

There are some smaller usability enhancements.

For more details, see the change notes for release 0.1.27 (below).


## Version 0.1.27, towards 0.1.28

- [x] BUG: 500: Server error: add_inferred_values_to_entity called with no type information available.
    - Changed calling enumeration logic to log a warning rather than error when referenced type is absent.
- [x] Provide option to remove type constraint when listing entities. ('All types' checkbox.)
- [x] Set default from list view: clear default view details so that default reverts to list
- [x] Update menu bar to indicate explicit/default type id.  Also list id.
- [x] Tweak CSS so that links in display columns wrap rather than overlap the next column
- [x] Re-work entity enumeration to avoid use of predefined built-in types. Fix some enumeration scope bugs.
- [x] Support references to uploaded OR linked images via subtyping.
- [x] When referencing fields of a target entity, include implied fields.
- [x] Adjust use of logging level settings in entity list view.
- [x] In FieldDescription, setup for value 'field_entity_subtypes' (~L150) - use `scope="all"`.
    - this allows values of subtypes inherited from other collections (or site-wide) to be included in selection drop-down boxes.
- [x] Place entity/view labels at start of page title for entity view, edit and list pages
    - Refactored entityedit for greater symmetry across GET/POST handling
- [x] Place list label at start of page title for lists
- [x] Entity save: If no label specified, default to ID with '_' replaced by space
- [x] Entity save: If no comment specified, default to label
- [x] Use site comment field to populate help panes on site front page; use Markdown.
- [x] Use collection comment field to populate help panes on collection edit display; use Markdown.
- [x] Use list definition comment to populate the help pane for a list display.
- [x] Use view definition comment as help text on forms
- [x] Add/update online help documentation to site data view/list definitions
    - [x] types
    - [x] views
    - [x] lists
    - [x] field groups
    - [x] enumerations (add label as header)
    - [x] user permissions
    - [x] vocabulary namespaces
- [x] Top menu bar vertical alignment: menu text to use common baseline
- [x] Use field comment text as tooltip on forms, to tell user how a field value is used
    - [x] Update renderer logic to include tool tips based on field help text
    - [x] Update test cases to avoid help-text sensitivity
    - [x] Added render type `Optional entity choice` for optional reference without edit button
    - [x] Update field help text
- [x] Add title attributes to buttons - used as tooltip
- [x] Create new field type for namespace/vocab id - label 'Prefix'


## Version 0.1.26

This release provides usability and presentation improvements, and some bug fixes.

The main change is support for a collection "default view" that can be a specific entity view.  This makes it possible to create a front page for a collection that provides a description and overview of the collection's content.

Other changes include:
- allow entity edit forms that do not include an entity Id field (i.e. always use default generated Id)
- renderers for fields that display non-editable text in entity edit mode
- `CodeArea` renderer, like `TextArea` but using a non-proportional font
- Some fields non-editable on collection metadata form
- Options to generate JSON-LD for list displays
- Reinstate continuation URIs on links from entity view and list pages:  this provides more consistent return to the previous page when closing entity list/view pages
- other small presentation and usability enhancements

For more details, see the change notes for release 0.1.25 (below).


## Version 0.1.25, towards 0.1.26

- [x] BUG: uploading PDF as image results in file extension PNG
- [x] BUG: "Server error" on save when repeat field references non-existent group id
- [x] BUG: can't save record using form without ID field
- [x] Home page: change button labels: "view metadata", "edit metadata", "remove collection".
- [x] Add read-only renderers for view short text and view markdown
    - `ShowText` and `ShowMarkdown`
- [x] Collection edit metadata page: make some fields display-only.
- [x] Add "Codearea" render type for unflowed, unformatted text with non-propo font
- [x] Content negotiation for alternative formats (initially just HTML (form), JSON-LD); others later.
    - [x] Content negotiation for entity view (e.g. `.../c/Carolan_Guitar/d/Artifact/Carolan_Guitar/`)
    - [x] Create view to generate JSON-formatted list of entities
- [x] Add "get the data" button to list display
- [x] In list view, provide scope as query parameter not path segment (i.e. `?scope=all`)
    - This allows relative URI references to work more cleanly.
- [x] Eliminate redundant modules `views.defaultlist` and `views.defaultedit` (but keep tests).
- [x] In drop-down list, include typeid/entityid only for entries whose labels are not unique.
- [x] Form field layout: arrange that fields lay out as indicated by the position value.
- [x] Create wiki-like view and allow use for collection fron page
    - [x] Expand collection view logic to allow default view display
    - [x] Add default view button to view template; update tests
    - [x] Add handler for default view button to entity view/edit handler
    - [x] Expand collection metadata to include default view details (view only)
- [x] Various new test cases
- [x] Reinstate continuation URI when following link in view or list (cf. commit f3f3001)
- [x] When accessing type without trailing "/", redirect to URI with. (Also for entity)
- [x] Review labels and IDs used when creating repeat fields and groups; suffixes defined in layout.py
- [x] When saving Id field, strip out any leading and trailing spaces


## Version 0.1.24b

This patch release fixes a data migration bug in the 0.1.24 release.  This bug meant that data from older releases was not being recvognized when accessed by the original 0.1.24 release.


## Version 0.1.24a

This patch release fixes a minor bug in the 0.1.24 release which sometimes caused one of the test cases to fail.  The fault was in the test suite setup rather than the Annalist software, but in the spirit of "no broken windows" is being fixed here.


## Version 0.1.24

This release adds sharing of collection structure descriptions, which is a first step towards supporting modularization of data structure descriptions.

An Annalist collection can be defined to inherit record type, view, list and other definitions from an existing collection.  This means a new collection can be created based on the structure of an existing collection, and then evolved as before.  Any changes that are made to the collection configuration are recorded in the new collection, and do not affect the original.  It will requiure some experimentation to work out how to best use this capability, but the current thinking is that the collection structure may be defined separately from the data, to be inherited by any collections that use the structure as a starting point.  (The structure descriptions can be extracted from an existing collection by copying the directory `c/_annalist_site` into a new collection.)

A number of bugs have been fixed, and there has been some extensive internal code refactoring, in part to prepare the codebase for separation of the record storage from the Annalist web service (e.g. to allow collections to be stored in separate Linked Data Platform servers).  For more details, see the change notes for release 0.1.23.


# Version 0.1.23, towards 0.1.24

- [x] BUG: resolve model dependency on view module introduced by context-generation logic
    - (caused Django configuration settings to be invoked too early, and spurious log output)
    - cf. TODOs in model.site and model.collection
- [x] BUG: `render_utils.get_mode_renderer`, handling of repeat fields? (cf. comment from Cerys.)
    - Added logic so that repeat fields also support current-mode rendering (but rendering as a normal view; i.e. with label)
- [x] BUG: enumerated values listed as types (when using "View all")
- [x] BUG: default view setting is not applied.
- [x] BUG (from 0.1.22 release): creating admin user in new site fails
- [x] Suppress display of _initial_values when listing entities (is this the right choice?)
- [x] moved 'child_entity_ids' method to root so it can be used with `Site` objects
- [x] moved site scoping enumeration logic from `Site` to `EntityRoot`
- [x] Re-work site/collection structure to allow cascaded inheritance between collections.  Eliminate site data as separate thing, but instead use a standard, read-only, built-in collection. This will    allow an empty collection to be used as a template for a new collection.  As with site data, edits are always added to the current collection.
    - [x] move annalist sitedata to special collection location
    - [x] re-implement SiteData as instance of collection; use this as collection parent; test
    - [x] re-work alternative-directory logic to be controlled by the parent rather than the child.
    - [x] add 'altscope' parameter to calls that may access the alternative search path (replacing `altparent` parameter)
    - [x] when creating a collection, allow to specify alternate parent(s); ensure no loops: must end up at sitedata; test
    - [x] ensure that _annalist_site collection cannot be removed
    - [x] implement search logic in Entity._exists_path, Entity._chidren, Entity._child_dirs, overriding methods from EntityRoot.
    - [x] remove all alt path/parent logic from EntityRoot
    - [x] change altparent parameter for altscope flag (None, "all", ...)
        - altparent is still used with Collection constructor to indicate alternative search path
    - [x] require Collection `altparent` to itself be a Collection.  Support later alteration of the `altparent`.
     - [x] Isolate all file access or file-dependent logic to EntityRoot (to simplify alternate storage later)
        - considered moving all remove file/path logic to EntityRoot and eliminating os.path inclusion in Entity, but still have directory path setup in Entity constructor.  The allocation of directory names is somewhat bound up with parent/child reklationships, so this limited file name handling logic remains in Entity.
- [x] Ensure that _annalist_site collection data cannot be updated
    - [x] Add new site permission map in model.entitytypeinfo that forbids modifications except users
- [x] Site data migration
    - [x] `annalist_manager updatesite` updated to create data in new location.
    - [x] `annalist_manager updatesite` copies previous users and vocabs to new location.
- [x] Updates to annalist-manager (createsite, updatesite): don't rely on sample data
    - [x] refactor site initializaton logic in models.site.py
    - [x] re-work am_createsite to use just models.site functions.
- [x] Provision for editing collection data (label, comment, parents, etc.); test
- [x] Re-think protections for viewing/editing collection metadata: really want the authorization to be based on permissions in the collection being accessed.
- [x] Create altscope="user" that skips alt parents and checks just local and site permissions
- [x] Provision for specifying and using inherited collections
    - [x] When loading a collection, add logic to set alternate parent based on specified parent in collection metadata.  Uses Collection.set_alt_ancestry
- [x] The bibiographic definitions currently part of site data moved to a "built-in" collection and inherited only when required (e.g., for certain tests).
    - [x] revise layout of site data in source tree to facilitate separate subsets (e.g. Bibliographic data)
    - [x] use new layout for site data to separate Bibliographic data from "core" site data
    - [x] copy bibliographic data collection into test data fixture
    - [x] update tests to work with biblio data in separate collection
- [x] Update JSON-LD spike code, and test with latest rdflib-jsonld
    - See: https://github.com/RDFLib/rdflib-jsonld/issues/33
    - [x] Add comment (generated by, date) to generated context files


## Version 0.1.22

This release puts "linked data" in the Annalist linked data notebook.  Up to this point, Annalist data has been stored and indirectly accessible as JSON, with Compact URI strings (CURIEs) used as key values for attributes.  This release augments the JSON data with auto-generated JSON-LD context files so that the JSON data can be read and processed as [JSON-LD](http://json-ld.org/#), hence loaded and processed with other data presented as RDF.

Also, the web pages for Annalist records now return links to the underlying JSON-LD data:

1. as "get the data" clickable links in the web pages,
2. as HTML `<link>` elements (with `rel=alternate` and content type attribute) in the web page header, and
3. as HTTP `Link:` headers (also with `rel=alternate` and content type attributes).

(Not implemented in this release, but intended for a future release, is HTTP content negotiation available on the primary URI for each entity record.)

Some bugs have been fixed, as noted in the version 0.1.21 summary.


## Version 0.1.21, towards 0.1.22

- [x] BUG: add a supertype while editing (copying) a new type loses any type URI entered.
- [x] BUG: create instance of type with defined type URI saves with `annal:type` value of `annal:EntityData`
- [x] BUG: renaming a group used by a view results in confusing Server Error messages (missing field)
- [x] BUG: (confusing interface) when local type/list/view overrides site definition, appears twice in dropdown lists.
    - include type/entity ids in drop-down lists; may want to review this choice later
- [x] Fix naming inconsistency: entity-data.jsonld should be entity_data.jsonld.
- [x] Content migration logic for entity-data.jsonld -> entity_data.jsonld
- [x] Linked data support [#19](https://github.com/gklyne/annalist/issues/19)
    - [x] Add `_vocab` built-in type that can be defined at site-level for built-in namespaces like `rdf`, `rdfs`, `annal`, etc., and at collection level for user-introduced namespaces.
    - [x] Define built-in vocabularies: RDF, RDFS, XSD, OWL, ANNAL
    - [x] Generate JSON-LD context descriptions incorporating the available prefix information.
        - site context data is created during installation as part of `annalist-manager updatesite`
        - collection context is created when collection is created
    - [x] Arrange to regenerate collection context when view/group/field/vocab are updated
        - [x] Implement post-update processing hook in EntityRoot
        - [x] Move context generation functions to collection class
        - [x] Define post-update hook for vocab, etc to regenerate context
    - [x] Arrange for context to be web-accessible via Annalist server
    - [x] When generating entity data, incoporate context information
    - [x] Add context references to site data
    - [x] JSON-LD context data test case (read as RDF using Python rdflib-jsonld)
- [x] Generate site JSON-LD context data as part of 'updatesite' installation step
- [x] Ensure that raw entity JSON is HTTP-accessible directly from the Annalist server, subject to permissions (e.g. <entity>/entity_data.jsonld.  Also for types, views, fields, etc.)
    - [x] coll entity data
    - [x] coll type data
    - [x] coll list data
    - [x] coll view data
    - [x] coll field data
    - [x] coll group data
    - [x] coll vocab data
    - [x] coll user data
    - [x] site type
    - [x] site list data
    - [x] site view data
    - [x] site field data
    - [x] site group data
    - [x] site vocab data
    - [x] site user data
- [x] Test cases to ensure JSONLD contexts can be accessed by HTTP.  
    - Collection and site, with correct relative location to entity data:
    - [x] entity -> collection context
    - [x] type -> collection context
    - [x] site-defined type -> site context
- [x] Add HTTP and HTML links to data to responses.  Also, link to data on view form.
- [x] Save 'annal:type' URI value in entity that matches corresponding type data.
- [x] Closed https://github.com/gklyne/annalist/issues/19


## Version 0.1.20

This release has tackled a number of usability issues, and in particular introduces a notion of "task buttons" that provide short cuts for some commonly performed collection configuration activities:
- creating view and list definitions for a new record type
- creating field and group definitions for a repeated field group
- creating field and group definitions for displaying fields from a linked record

Other changes include:
- Simple links no longer include continuation URIs.  This means that the link URLs are more consistently usable as identifiers.
- Missing entity links are rendered in a more distinctive style.
- Closing top-level list displays no longer return to the site home page, but rather redisplay the collection default view.  This has the effect of making collections more "sticky" in the sense that a user is less likely to find they are unexpectedly looking at some completely different data collection.

It also fixes a number of bugs, including several introduced by the new logic to allow lists to include subtypes in release 0.1.18.  (This change meant that the way entity references is handled is fundamentally changed, and a few required updates were overlooked and missed by the test suite.)  See the version 0.1.19 task summary for more details.

An [Annalist tutorial](http://annalist.net/documents/tutorial/annalist-tutorial.html) document has been created.  It is still in a very drafty form, but it provides a more task-oriented desription of Annalist capabilities.  There is a generated HTML document and associated resources in directory `documents/tutorial/annalist-tutorial` of the distribution kit.  A copy has been placed online at [http://annalist.net/documents/tutorial/annalist-tutorial.html]().  A [rough rendering](https://github.com/gklyne/annalist/blob/develop/documents/tutorial/annalist-tutorial.adoc) of the latest working draft can be viewed directly from the Annalist Github repository.


## Version 0.1.19, towards 0.1.20

Usability: key tasks need to be easier (at the level of a single form fill-out):
- Create a new type+view+list, suitably interconnected
- Create repeating fields in a view
- Create multifield reference in a view/group
- See also: [#41](https://github.com/gklyne/annalist/issues/41)
- See also discussion below of introducing generic "tasks" - this would be an early pathfinder for that.

- [x] BUG: view types > view type > task button > (error) > Cancel.  Returns to type list rather than view of edited type.  Fixed up some probvlems with continuation URI generation.
- [x] BUG: extend render placement to handle list columns defined for small only
- [x] BUG: unclosed <div> in RepeatGroupRow renderer was causing formatting errors.  (Ugly but not fatal.)
- [x] BUG: `<form action="" ...>` fails HTML validation.  Use `action="#"` instead.
- [x] BUG: attempting to create new referenced entity while current entity Id is invalid gives a very obscure server error message (message with Save is sort-of OK).
- [x] BUG: Edit referenced field button in edit view doesn't work if entity type has been changed to subtype.
- [x] BUG: image with placement (0/8) displays incorrect label size.   Remove field placement options x/8 or x/9 (not sub-multiple of 12).  These widths are still allowed for columns.
- [x] BUG: "Define view+list" error when defining a new type; remember when entity has been saved and skip existence check when performing a subsequent save. Added `DisplayInfo.saved()` method.
- [x] When rendering missing entity reference in view mode, use alternative style/colour
- [x] Don't include continuation URI with entity links in list, view, etc.?
- [x] Create a new type+view+list, suitably interconnected
    - [x] Add task-button description to view description for type; use structure for repeat values: for each: Button Id, button label
    - [x] Render task buttons on view (generic logic)
    - [x] Add logic to catch and dispatch view+list task-button click
    - [x] Add logic to create/update view+list from type form data - hand-coded for now, but subsequent implementation may be data-driven.
    - [x] Create test case(s)
- [x] Create repeating fields in a view.
    - [x] Add task button to field definition form: define repeat field
    - [x] Add logic to catch and dispatch define-repeat click
    - [x] Add logic to create repeat group that references current field
    - [x] Add logic to create repeat field that references group
    - [x] Create test case(s)
- [x] Create multifield reference fields in a view or group.
    - [x] Add task button to field definition form: define field reference
    - [x] Add logic to catch and dispatch define-multifield click
    - [x] Add logic to create multifield group that references current field
    - [x] Add logic to create multifield reference field that references group
    - [x] Fix up formatting for reference field not in a repeated group
    - [x] Create test case(s)
- [x] On closing top-level list display: return to collection default view, not Home.  This has teh effect of keepinbg the user within a single collection unless they explicitly select `Home` from the menu bar.
- [x] Change "List users" heading to "List user permissions"
- [x] Initial tutorial/task-oriented documentation. Uses personal photo library example.


## Version 0.1.18

This release introduces several interface changes to address usability problems, 
bug-fixes (many associated with resource import/file upload logic), and embodies 
some fairly extensive changes to the internal code structure.

New features include:
* an option to reorder repeated field entries in a view (via move up/down buttons)
* ability to declare simple type hierarchies with different presentation of subtypes.  
Lists of a given type also include any subtypes.  
Consistent with the Annalist philosophy, type hierarchies can be adjusted 
dynamically and are not baked in to the data storage structure.
* option to edit existing referenced values from entity edit view, 
in addition to creating new values.
* in entity edit view, entity-reference dropdown lists display labels rather
than internal entity Ids, which it is hoped will lead to more user-friendly 
presentation when creating and editing entity data records.

(More details are given in the release notes change summary for version 0.1.17)


## Version 0.1.17, towards 0.1.18

- [x] Option to re-order fields on view form: add move-up/move-down buttons
- [x] Multiple URIs for type, and instances of type - add "supertypes" field
      to type description, and propagate these to the @types field of created 
      instances.
- [x] List of type also includes subtypes
- [x] Dropdowns to select value of type also presents subtypes
- [x] When using "+" to add an enum entry, also provide quick route to edit entry.
    - [x] when existing item is selected, change button label "+" to "writing hand" (&#x270D;)
    - [x] when button is clicked, edit existing value if selected.
- [x] Enumerated selection - include labels rather than Ids in dropdown

- [x] Introduce separate data-compatibility version (may lag current version).  
This means that older software may continue to work with newer data when 
no compatibility-breaking changes are introduced.
- [x] _group annal:record_type fields updated to treat grouped field 
description data as separate record type.
- [x] Confirmation message when resource is imported/uploaded
- [x] Missing enumerated value reference: provide better diagnostic
- [x] Missing enumerated value field: display diagnostic instead of blank
- [x] Remove redundant field render types (Type, List, View, Field, etc.)
    - keep entries in render_utils for backwards compatibility

- [x] BUG: if alternative field is defined for "Entity_id" (e.g. for different label), 
can't save entity, because internal expected form of field name was not used.  
When RenderType is "EntityId, force use of standard field name.  
Similar for "EntityTypeId".
- [x] BUG: if Value_entity field does not include "refer to type" value, 
barfs with 500 error.
- [x] BUG: Multifield ref inside a repeat field not occupying the entire 
width of the field generates messed up layout of labels vs content.  
Added an additional layer of row/cols for the headers of the 
multifield reference.
- [x] BUG: import resource in new entity raises internal error
- [x] BUG: import image when new or changed changed record ID gives error
- [x] BUG: import image when changing record ID causes error on save
- [x] BUG: if multiple repeated field groups are selected for deletion, 
only the last is deleted
- [x] BUG: follow links to edit view, then save, does not return to entity view.

- [x] Internal refactoring of error handling and reporting via "responsinfo" structure
- [x] Built-in `Entity_id` and `Entity_label` fields position/size values updated
- [x] Revise add field buttons to use save+redirect rather than re-render
- [x] Use responseinfo values for status reporting to user
    - changes made for save and import.
    - other changes to be applied as the need arises.
- [x] When testing site data, additional consistency check that entity type of 
repeated field matches with value type of referencing field and group
- [x] Add test cases for references to type with subtypes defined: 
check that subtype instances are also presented.
- [x] Add/update test cases for selecting entity type
- [x] Add/update test cases for selecting entity view
- [x] Add/update test cases for selecting entity list
- [x] Update site data to ensure new enumerated-value logic is tested
- [x] Small improvement of performance for collection type access
- [x] Small improvement of performance for test suite setup


## Version 0.1.16

The main advances in this release are improvement of the file upload and resource import logic, and improvements to the form rendering to make it easier to use media attachments.  One strategy adopted is to use an entity type as a "media library" to which resources can be attached, and to provide new field rendering options to reference the attached resources and associated metadata.  These new capabilities have been used to enhance the picture displays in the "CruisingLog" demo collection at http://demo.annalistr.net/ (see definitions for `DailyLog`, `Place` and `Picture`).

Other changes include:

* Support for audio clips
* General rationalization of some aspects of the form rendering logic
* More test cases
* Documentation updates


## Version 0.1.15, towards 0.1.16

- [x] create picture gallery demonstration collection to test file uploads
- [x] BUG: file upload when creating entity appears to not work; need to create first then upload.
- [x] ensure attachments are moved when entity is renamed.
- [x] test cases for upload image displayed in same entity, rename with attachments, edit entity with attachment
- [x] file upload view/edit: display uploaded filename as well as link
- [x] rename render type URIImage as RefImage; update documentation
- [x] allow multiple fields displayed from referenced entity (e.g. image for file upload).
- [x] add render type RefAudio (use embedded HTML player); update documentation
- [x] rationalize field description form to make handling of upload/import and references to fields in other entities more obvious
    - [x] Add `field_value_mode` to field description
    - [x] Add migration logic to set `field_value_mode` appropriately in field definitions
    - [x] Change some field labels
    - [x] Rename FieldDescription method `has_import_button` to `is_import_field`
    - [x] Use `field_value_mode` to determine `is_import_field` and `is_upload_field`
    - [x] Find all references to `field_value_type` and change logic to use `field_value_mode`
    - [x] Remove references to `field_ref_type` when selecting renderer (`get_edit_type`, others?)
    - [x] Remove 'field_value_type' from `FieldDescription`.  Update all tests to use 'field_target_type'
    - [x] Add 'field_value_mode' to all field descriptions in site data and some example data
    - [x] Remove `annal:Import` and `annal:Upload` as instances of `field_value_type` in site and demo data
    - [x] Update all references in code to 'annal:...' value types to use ANNAL.CURIE.... values instead
- [x] Update documentation (including README.md status summary)


## Version 0.1.14

The big change in this release is inital support for imported web resources and uploaded files within an Annalist collection.  These are captured as "attachments" to an entity via field render types `URIImport` or `FileUpload`.  The attachments can then be referenced via the entity to which they are attached, also specifiying the field property URI: see `documents/view-field-types.md` for more details.

The new facilities for presenting uploaded and imported files still need some work, and some code refactoring will be needed to make handling of such references more consistent.

A number of bugs have been fixed, and other features added or improved:

* Add logic to serve content of entity attachment in orginally submitted form.
* Add "View" button to entity edit form.  This makes it possible to show hyperlinks that can be used to access referenced entities.
* Fix some situations causing "500 Server error" messages.
* Update continuation URI if necessary when an entity is renamed.
* Added software version to collection, and refuse access if collection version is higher than current software version.
* Don't save `annal:url` value in stored entities; rather depend on its value being determined when an entity is accessed.  This potentially improves portability of data collections.
* Add documentation of view field descriptions, particularly to cover fields that are used to create entity attachments.
* Added internal support for complex field values that can be partially updated (used to support attachment metadata).
* Quite extensive code refactoring to support attachments.
* Added hooks for file format migration.


# Version 0.1.13, towards 0.1.14

- [x] BUG: invalid entity id in field data causes 500 ServerError
- [x] BUG: if field group refers back to orinal field, python blows its stack, reports 500 ServerError
- [x] Improve reporting of 500 serverError
- [x] BUG: edit from view, change id, results in NOT FOUND error displayed when returning to previous view.  This occurs because the continuation URI is refers to the old entity when the id is changed.
    - treat id/type change as special case and update all matching URIs in the continuation chain.  This involves dismantling and reassembling the continuation URI, and the continuation URL handling logic has been refactored to facilitate this.
- [x] Support for complex entity field values (e.g. supporting details for resource imports)
    - [x] Refactor entityedit Save_Entity handling
    - [x] Refactor entityedit to carry more context in viewinfo (simplify function calls)
    - [x] Refactor value decoding so it can access other form fields (to build complex values)?  (see next)
- [x] Blob upload and linking support [#31](https://github.com/gklyne/annalist/issues/31)
    - [x] Blob and file upload support: images, spreadsheets, ...
        - [x] Choose render type name: URIImport
        - [x] Define renderer test cases as a new module in `annalist/tests/`, e.g.:
            - [x] Copy `test_render_bool_checkbox.py` to new module name
            - [x] Update descriptive comment at top of module
            - [x] Update `import` statement to refer to new module to be defined
            - [x] Update class name
            - [x] Rename and update the test case method for value rendering: this should cover value view and edit cases as appropriate.
            - [x] Rename and update the test case method for decoding input values suitable for storage in a JSON structure.
        - [x] Define a new renderer module in `annalist/views/fields/`; e.g.:
            - [x] Copy `render_bool_checkbox.py` to new module name
            - [x] Update descrptive comment at top of module
            - [x] Update class name for value mapper
            - [x] Implement value mapping as required.  If the values do not require mapping between the JSON object and form data, the class `render_text.RenderText`, which contains identity mapping functions, can be used instead.  If the renderer updates the JSON representation of existing data, consider handling legacy representations in the `encode` method to facilitate data migration.
            - [x] Rename and update the view renderer and edit renderer functions to generate appropriate HTML.
            - [x] Rename and update the get renderer function.  Note that this function must returned a `RenderFieldValue` object, as this provides the interfaces required by the rest of Annalist to render values in different contexts.
        - [x] Update entityedit.py to recognize new action to import resource
        - [x] Add tests for file import (needs to be a "full stack" test - see `test_field_alias` or `test_linked_records` for simple form of structure to follow)
        - [x] Edit module `annalist/views/fields/render_utils.py` to import the get renderer function, and add it to the dictionary `_field_get_renderer_functions`.
        - [x] Add the renderer type name to the enumeration defined in `annalist/sitedata/enums/Enum_render_type`
        - [x] Update the test modules to accommodate the new render type, and retest:
            - [x] `annalist/tests/test_entitygenericlist.py` about line 244 (bump counter)
            - [x] `annalist/tests/entity_testsitedata.py`, about line 306 (add new render type name in sorted list)
        - [x] Check the affected web views and augment the site CSS file (`annalist/static/css/annalist.css`)
    - [x] Field definition enhancements to link to uploaded file
        - [x] Design revised field definition structure to separate rendering from value reference
            - [x] Value reference direct
            - [x] Value reference as upload to current entity
            - [x] Value reference as URI
            - [x] Value reference as field of another Annalist entity
        - [x] Review existing render type definitions in light of new design
        - [x] Work out migration strategy for collections to use new field structure
        - [x] Revise field render selection logic to allow separate edit renderer selection from view renderer selection
            - Updated logic in maily in render_utils, but some interfaces are revised affecting fielddescription, etc.
        - [x] Revise field value handling to take account of multiple sources
        - [x] Figure out how to resolve relative references: based on entity URL?
        - [x] Test, test cases
        - [x] Refactor: change field names in field description. 
            - [x] s/field_options_typeref/field_ref_type/
            - [x] s/field_restrict_values/field_ref_restriction/
            - [x] s/field_target_key/field_ref_field/
            - [x] s/annal:options_typeref/annal:field_ref_type/
            - [x] s/annal:restrict_values/annal:field_ref_restriction/
            - [x] s/annal:target_field/annal:field_ref_field/
        - [x] Apply updates to site data as needed
        - [x] Add logic to migrate collection data
            - [x] Add migration hook to Entity.load() method - call self._migrate_values()
            - [x] Default _migrate_values method in EntityRoot just returns with no change
            - [x] Attach migration data/method to EntityData subclasses as required.  May include common logic in EntityData method.
            - [x] s/annal:options_typeref/annal:field_ref_type/
            - [x] s/annal:restrict_values/annal:field_ref_restriction/
            - [x] s/annal:target_field/annal:field_ref_field/
        - [x] Add field ref to field view form
- [x] Add 'view' button to edit form
- [x] Add file-upload option (with resulting value like URI-import)
    - Cf. https://docs.djangoproject.com/en/1.7/topics/http/file-uploads/
- [x] Serve reference to uploaded or imported resource.  Content-type and other infiormation is saved in a URIImport or FileUpload field value that is a dictionary.
- [x] Test cases for file upload
    - [x] test_render_file_upload (adapt from test_render_uri_import)
    - [x] test_upload_file (adapt from test_import_resource)
- [x] Create field definition for referencing uploaded image file - use URIlink render type
- [x] Test case for referencing uploaded file
    - [x] Similar to Import test
    - [x] View rendering test with reference to uploaded file 
        - (Use URIImage for manual test, then create test case)
        - need to extract resource_name from target field value for link...
- [x] Sort out file upload view rendering
- [x] Add test case for simple image URL reference rendering (no target link)
- [x] Add software version to coll_meta.
    - [x] Add when creating collection
    - [x] Check this when accessing collection.
        - cf. http://stackoverflow.com/questions/11887762/how-to-compare-version-style-strings
            from distutils.version import LooseVersion, StrictVersion
            LooseVersion("2.3.1") < LooseVersion("10.1.2")
        - accessing collection:
            - Check version in DisplayInfo.get_coll_info()
    - [x] Update when updating collection
            - tie in to entity save logic.
- [x] Is it really appropriate to save the annal:url value in a stored entity?
    - [x] in sitedata/users/admin/user_meta.jsonld, not a usable locator
    - [x] entityroot._load_values() supply value for URL
    - [x] entityroot.set_values only supplies value of not already present
    - [x] entityroot.save() discards value before saving
    - [x] views/entityedit.py makes reference in 'baseentityvaluemap'.  Removed; tests updated.
- [x] Update documentation to cover import/upload and references.


## Version 0.1.12

The substantial change in this release is the introduction of non-editing entity views, with rendering of links to other referenced entities.  This makes it very much easier to navigate the network of entities that make up a collection.  A number of new render types have been introduced, many to support more useful data display in the non-editing view (links, Markdown formatting, etc - more details below.).  This non-editing view is now the default display for all entities.

This release also contains a number of usability enhancements and bug fixes, including:

* Save logs in root of annalist_site data, for Docker visibility.  When Annalist is running in a Docker conainer, another container can attach to the same data data volume in order to view the server logs (see the [installation instructions](https://github.com/gklyne/annalist/blob/master/documents/installing-annalist.md) for more information about how to do this).
* New render type: Boolean as checkbox
* New render type: URI as Hyperlink
* New render type: URI as embedded image
* New render type: long text with Markdown formatting; and new CSS to style Markdown-formatted text.
* Page layout/styling changes; rationalize some CSS usage to achieve greater consistency between the editing, non-edit and list views.
* Change 'Add field' button to 'Edit view' - this switches to the view editing page where field definitions can be changed, added or removed.
* Add 'View description' button on non-editing entity views - this switches to a display of the view description.  Subject to permissions, an 'Edit' button allows the view definition to be edited.
* View display: suppress headings for empty repeatgrouprow value.
* Preserve current value in form if not present in drop-down options.  This change ws introduced mainly to prevent some surprising effects when editing field descriptions; the change is partially effective, but there remain some link navigation issues when a field value of not one of those available in a drop-down selector.
* Various bug fixes (see below)


# Version 0.1.11, towards 0.1.12

- [x] Minor bug: in DMO_experiment, add new performer field, click "+" to define new performer, on return to previous page new field is not there.  Suspect it is because all fields are blank when "+" is clicked, so new field not saved.  Modified `views.form_utils.fieldvaluemap` to treat only `None` as non-existent field value.
- [x] Configuration change so that shell session in new Docker container can see server logs.  Save logs in root of annalist_site data.  
- [x] Non-editing entity view: [#3](https://github.com/gklyne/annalist/issues/3)
- [x] New render type: Boolean (checkbox) [#2](https://github.com/gklyne/annalist/issues/2)
- [x] Document process for creating and integrating a new renderer
- [x] New render type: Link (hyperlink) [#2](https://github.com/gklyne/annalist/issues/2)
- [x] New render type: Image, [#2](https://github.com/gklyne/annalist/issues/2)
- [x] Extend CruisingLog example data with image galleries for place and daily log entries
- [x] New render type: Markdown, [#2](https://github.com/gklyne/annalist/issues/2)
    - [x] Markdown test cases
    - [x] Markdown renderer
    - [x] Fix up CSS for Markdown formatting; e.g.
        - div.columns.view-value > span.markdown p
        - div.columns.view-value > span.markdown li
        - div.columns.view-value > span.markdown h1
        - div.columns.view-value > span.markdown h2
        - div.columns.view-value > span.markdown h3
        - div.columns.view-value > span.markdown h4
    - [x] Update Annalist dependencies to include markdown package
    - [x] Update site data to use Markdown where appropriate 
- [x] Fix styling (row spacing) for site front page - it looks a bit spaced-out following changes to view/list styling.  probably just needs appropriate new CSS classes to be included.
- [x] Beside the "Add field" button, include "Edit view" button on entity editing page.
- [x] BUG: RepeatGroupRow field without Group Ref specified gives 500 error when view is displayed
- [x] BUG: no substitute if add/remove labels not supplied
- [x] Field placement lacks 0/9, 3/9, 0/8, 4/8, 3/6 options
- [x] Provide image click-through to larger version.
- [x] Replace the "Add field" button with an "Edit view" button
- [x] Add "Edit view" option to view as well as edit form
    - View description doesn't carry the entity Id to the continuation URI (None instead)
- [x] View display: suppress headings for empty repeatgrouprow value
- [x] Entity drop-down selectors: add current value to list if not already present
    - (avoids hiding information if type URI changed and field type is no longer offered)
    - Done, but when a field is not available for a view, there is no link provided to edit it.


## Version 0.1.10

This release contains a number of usability enhancements and bug fixes, including:

* Option to create new linked record from referring record view.  This means, for example, when creating a view description that the field selector drop-downs have an additional "+" button that can be used to create a new field type definition.  This feature is provided for all enumerated value fields that refer to some other entity type.
* Add field alias option.  This allows record-specific fields to be returned as the value for some other property URI;  e.g. in bibliographic records (`BibEntry_type`), the `bib:title` field can be used for `rdfs:label` values, and hence appear in views that expect `rdfs:label` to be defined.
* When changing a list view, don't filter by entity type.  Previously, when listinging (say) all `_type` entities, and changing the list type to `View_list`, no entries would be displayed because of conflicting entity selection criteria.
* Use more obvious interface for displaying collection only vs collection+site entity listings.  Previously used an explicit type id in the URI to display collection+site data; now uses `View` vs `View all` buttons to display collection-only or collection+site data respectively.
* Use placholder as descriptive label for repeated group form display.
* Implement special renderer for field placement (position/size)
* Rework handling of repeated use of same field.  In previous releases, having the same field type appear more than once in a view description could lead to unexpected happenings when editing an entity.  This is now fixed by ensuring that a unique property URI is used for each one.
* `annalist-manager` enhancements; permissions help, new information subcommands
* Document default admin user permissions created with new site
* Various bug fixes
* Form display and response code refactored to make code easier to undertsand, and ease future maintenance and exhancement of the code base.
* Refactor field rendering logic for better support of more complex field rendering options (cf. field placement).
* Added build scripts for Docker containers, and add Docker-based installation instructions.


## Version 0.1.9, towards 0.1.10

- [x] Bug: https://github.com/gklyne/annalist/issues/39 (hotfix 0.1.8a)
- [x] Add mechanism to alias a common field (e.g. rdfs:label) to return some other specified field value (e.g. bib:title).  Associate aliases with record type, used when constructing view/list context.
- [x] Option to create linked record directly from other record entry field (issue #23). Propose enum type renderer should include a "New" button that launches new view to enter new value of appropriate type.
    - [x] Add new logic in views.entityedit
    - [x] Create enumeration renderer: update template or replace with renderer class to add extra "New" button to enumerated value fields
    - [x] Create test case for new option (should be able to adapt, e.g., "New view" test case?)
    - [x] Create test case for new button on field selector in _view edit
- [x] BUG: View property-override in field list is not working, or is not recognized by by the duplicate property check.  See also issue (below) about 'Add field' followed by 'New field'.
- [x] BUG: '+' button on repeated field value creates entity of wrong type: e.g. _type not Place.  Was bug in enumeration scanning logic.
- [x] BUG: Add segment in CruisingLog gives 500 server error.
- [x] BUG: annalist-manager updatesitedata not clearing out old enumeration types.  Not there.  See next.
- [x] BUG: pip uninstall not clearing out old sample data, causing test failures.  Looks like a problem with the build process, not clearing out old files.  How to fix?
    - python setup.py clean --all
- [x] BUG: ID too long is accepted but then can't access (404 response).  Need to id validity check before saving.
- [x] Refactor button locating logic in edit form response handler
- [x] Refactor and clean up entity save code in edit form response handler
- [x] Review field description is_enum_field - use `has_new_button` for fields with `new` button
- [x] review field description and detection of repeated field-group references. 
- [x] Select new list view: drop type_id from URI? (e.g. when changing to view of different type)
- [x] Consider use of "hidden" flags on views, types, fields, etc. to avoid cluttering UI with internal details?  The current mechanism of using an explciit type to display site-wide values is probably confusing.
    - Implmentation adds 'scope' flag to list URIs (!all), and adds "View all" button to list views to select the wider scope.
- [x] 'New' and 'Copy' from list view should bring up new form with id field selected, so that typing a new value replaces the auto-generated ID.
- [ ] Consider removing "New type", "New view" and "New field type" buttons, but keep corresponding test cases so they can be reinstated).  Tie logic in to new enumerated-value handling.
    - [x] refactor logic for new-entity from entity edit view
    - [x] rename 'View_repeat_fields' back to just 'View_fields'
    - [x] hide new type, view, field type buttons in edit template
- [x] Usability issues arising from creating cruising log (see next item)
    - [x] 'Add field' can't be followed by 'New field' because of duplicate property used
        - consider using Enum_optional logic so the field selector id isn't automatically filled in;  ignore blank field ids when processing;  ensure field with blank id is still saved with view/group.
        - chosen fix is to auto-generate a property URI in the view description based on the field property URI but with a _2, _3, etc suffix.  If there is an existing view-defined property URI that clashes, reject the update as now.
        - what to do if the render type is changed?  Ideally, remove any auto-generated property URI, but preserve manually entered values.
    - [x] Entity edit view: "New field" -> "New field type"
- [x] BUG: save entity where view has same field id with different properties is not working properly.  Second value is saved to both fields.  It turns out the field property URI in view description is only a partial fix to the duplicated fields problem, and the approach needs to be re-thought.
    - [x] Verify problem in test case - TestEntityEditDupFieldTest
        - [x] Create a view with duplicate field id
        - [x] Create entity with values for duplicate field id - the exact representation will be up for grabs.  For now use suffix for those after the first - later may consider using a list of values.
        - [x] Render entity in view, check context used to generate form.
        - [x] Submit form with values for duplicate fields.  Again, the exact representation will be up for grabs, but for now use a suffix for fields after the first.
        - [x] Will need function to create test entity data with dup field vals; this will isolate representation of dup fields in an entity
        - [x] Will need function to create test form data with dup field vals; this will isolate representation of dup fields in a form
    - [x] Fix problem.
        - [x] Introduce suffix into FieldDescription when building EntityValueMap.
        - [x] Update field_name and field_property_uri values to include suffix.  Also add acvcess functions.
        - [x] No error if field definition is repeated in view (or group).  (Good - that code was pig ugly!)
        - [x] FieldListValueMap invoke conflict resolution logic in FieldDescription.
        - [x] Where possible, replace direct access to field name and property URI to use new access methods.  (bound_field still uses direct indexing because test code uses faked FieldDescription structure.)
- [x] RepeatGroup renderer - use placeholder beside label as way to explain content?
- [x] Implement renderer for field placement field
- [x] Revise tokenset renderer to follow field placement pattern; get rid of encode/decode methods?
- [x] Rationalize storage of repeat_prefix in context: top level or under 'repeat'?
- [x] Review options for creating user accounts in development software version (currently have 'admin'/'mailto:admin@localhost' in sitedata as holding option).  Put something explicit in makedevelsite.sh?  Document site 'admin' user and development setup?
    - For now, sticking with admin user entry in initial site data.  Updated install document.
- [x] Remove `/annalist_root/sampledata/data/` from distribution kit data so that test suite can run in Docker container.  (Otherwise, can't rename old data directory due to "Invalid cross-device link" error)
- [x] `annalist-manager` help to provide list of permission tokens
- [x] `annalist-manager` createsitedata should also create collections directory
- [x] `annalist-manager` option to write version string to stdout
- [x] docker installation files and scripts, and docker container available from dockerhub
- [ ] Installation instructions need to be clear (and tested) about ordering of create, initialize, defaultadmin
    - final check when creating new release.


## Version 0.1.8a

This is a patch release for bug https://github.com/gklyne/annalist/issues/39.  This bug causes a server error to be reported if a user logs in with an ill-formed user_id.

## Version 0.1.8

The main new feature in this release is full support for views containing repeated fields (e.g. a bibliographic entry containing multiple authors).  These can be displayed as a repeating group of fields formatted similarly to non-repeating fields (`RepeatGroup` render type) or as a repeating row of values with column headings (`RepeatGroupRow` render type).  With this enhancement, the core web presentation engine is substantially complete, with further capablities to be provided by adding new field renderers.

Other changes are a substantial reworking of the form-generating and handling engine used for data display and entry, numerous small bug-fixes and enlargement of test coverage.

Summary of other improvements and bug-fixes:

* Added field groups as part of support for repeating fields in a data view.
* Updated sample descriptions of bibliographic data to use repeatinbg field groups, to fully support BibTeX/BibJSON-like structures.
* Update annalist.net demo site front page (see `documents/pages`).
* New test suite to check completeness and consistency of site-wide data.
* Fixed some bugs in field type selection when editing view descriptions.
* View generating code regorganization and rationalization.  Most of the HTML form-generating code is now in a separate code directory.
* Unification logic used to generate entity list displays and repeating fields in an entity view/edit form.
* Formatting, generated HTML and CSS changes; eliminate use of HTML `<table>`.
* Fix server error when copying view without URI field (also hotfix 0.1.6a).


# V0.1.7, towards V0.1.8

TODOs completed:

- [x] Add "get the data" button to annalist.net page: https://github.com/BetaNYC/getDataButton
- [x] Extend form-generator capabilities [issue #2](https://github.com/gklyne/annalist/issues/2)
    - [x] Revise representation of repeat field structures in view description: repeat description to be part of root of repeat structure, not an ad hoc field at the end.  This should remove some special cases from the code.
    - [x] Refactor handling of repeat field groups
    - [x] Define type for field group (_group?  Or use _view?)
    - [x] Use _list rather than _view? (NO: list has much more bound-in semantics)
        - NOTE: in debugging, a new built-in type has been introduced to provide better control over UI elements.
    - [x] Rename 'View_field' to (say) 'View_field_view' (cf. previous use _list)
    - [x] Define view for field group (list of fields)
    - [x] Define list for field groups (not needed as views used for field-groups)
    - [x] Redefine view with list of fields?  Not if that impacts usability.
    - [x] Define e-v-map for defined list of fields
    - [x] Repeat to reference list of fields 
- [x] Eliminate duplication with list view - rework list to use same repeating mechanism as view
- [x] Provide clean(er) mechanism to propagate extra context to bound fields in repeat group rendering
- [x] Try eliminating `view_context` parameter from `FieldListValueMap` constructor
    - it turns out that it's needed for generating enumerated type lists based on target type of view, but code has been rationalized and slightly simplified and relevant comments added.
- [x] Use distinguished names for internally-generated context keys (e.g. '_fields')
- [x] Simplify list template now that repeat fields are handled by a field renderer
- [x] Make mapping classes more consistent in their return types for sub-context values
- [x] Raise error if required view_context information is missing for EntityFinder
- [x] Add field for `annal:field_entity_type` property in field view
- [x] Revisit definitions for BibJSON view; confirm that repeat field groups can be created
    - [x] Bib_type field should be enumeration
    - [x] Month, year on same line
    - [x] Restrict view choices field to views that are not subsidiary field groups
- [x] Improve list column layout, avoid values overflowing column and overlapping next (e.g. with long identifiers - cf. http://localhost:8000/annalist/c/coll1/l/Default_list_all/_view/) (PART FIX - made id column wider)
- [x] Improve display of view fields: put field names in header of repeat-group
    - [x] Reworked field rendering to support more options
    - [x] List display remove header rendering from template, handle in repeat
        1. [x] Put header column logic in repeat group item renderer
        2. [x] Update list template
    - [x] Introduce new render type RepeatGroupRow, sharing code with RepeatGroup
    - [x] Move row selection from template (uses .item) to editlist (uses RepeatGroup)
    - [x] Work through field rendering options for RepeatGroupRow:
    - [x] Rework field description used by view view to use new field rendering options
- [x] merge rework-form-manager to develop branch
- [x] Bugfix: e.g. 'Bib_person_field_view' does not show appropriate field options
- [x] Bug: create field group does not show up on field group list
- [x] Need test coverage for FieldDescription with a field group
- [x] Tests for sitedata: using Beautifiul soup (maybe), create table-driven tests for checking field contents for various rendered pages (lists and views), abstracted away from finer details of rendering and layout.  For example, test that correct field options are displayed for different views.
    - [x] Move site data functions from entity_testentitydata to entity_testsitedata
    - [x] Add functions for groups
    - [x] Define new test_sitedata module with functions for testing values in view rendering via BeautifulSoup
    - [x] Create test cases for each of the main views on site data
    - [x] Remove tests from other test sites that duplicate these tests (esp test_record* tests) (do this later, progressively)
- [x] Test software installation from merged branch
- [x] Hand-test new capabilities to define view with repeating fields - make sure it is doable
- [x] Test adding more data to cruising log sample data
- [x] Rename: Field_sel Group_field_sel (option for Field_group_view only)
- [x] Copy: Field_property, Field_placement -> Group_field_* (options for Field_group_view)
- [x] Test upgrade of existing deployment
- [x] Deploy updates to annalist.net


## Version 0.1.6

The main new feature in this release is an authorization (access control) framework;
There are also numerous small improvements and bug-fixes:

* Implemented authorization framework
* Updated `annalist-manager` to set up initial/default perissions needed to start working with Annalist
* More new commands in `annalist-manager`
* List view option to hide columns on smaller screens (cf. permissions)
* Extend test suite covereage
* When adding field to view: check property URI is unique
* Documentation updates and new screencasts
* When renaming type, rename insrances to new type
* Prevent deleting type with instances present
* If specified default list not found, revert to built-in default
* Fix bug in entity reference field links (was linking to self, not target record)
* Add optional enumeration to available field render types
* Use separate Django database for each configuration
* Improve log file handling; include timestamps
* Some small usability improvements
* Address some areas of technical debt

## Version 0.1.5

TODOs completed:

- [x] Authorization [#11](https://github.com/gklyne/annalist/issues/11)
    - [x] layout.py: add _user defs
    - [x] message.py
    - [x] entitytypeinfo.py
    - [x] annalistuser.py (new)
    - [x] AnnalistUser test suite
    - [x] create _user type
    - [x] collection.py - just get_user_perms method for now.
    - [x] get_user_perms test case in test_collection
    - [x] add method for getting details of current authenticated user (GenericView).
    - [x] update authorization method calls to include target collection
    - [x] Use user id to locate, but also check email address when granting permissions.
    - [x] Create generic view method for accessing user permissions (may supersede collection method)
    - [x] Provision for site-wide default permissions
    - [x] Authorization test suite
    - [x] update authorization logic to use permissions data
    - [x] create collection also creates initial user record for creator with all permissions
    - [x] annalist-manager create admin user also needs to create site admin permissions for that user
        - Note: required change to create Django user programmatically rather than by django-admin utility
    - [x] view description for user
    - [x] field descriptions for user
    - [x] field rendering: logic to decode value entered; e.g. for token list
        - [x] new user rendering tests
        - [x] existing user render tests
        - [x] existing user update tests (post edit form) - focus on resulting permissions field
        - [x] move get_entity_values from 'render_utils' to 'bound_field'
        - [x] WONTDO update code to use class for simple text rendering
            - NOT YET: current structure doesn't distinguish between edit, view, etc.
            - Resolve that before updating existing use of separate template files
    - [x] user view: change stored permissions to list
        - clarify JSON-LD behaviour for treatment as set vs sequence
        - see: http://www.w3.org/TR/json-ld/#sets-and-lists
        - e.g. { '@list': ['a', 'b', ... ] }
        - but note: JSON-LD default is to treat as set, which is OK for permissions:
        - [x] Rename TokenList -> TokenSet
    - [x] new field render option: annal:field_render_type: TokenSet (with value_type annal:TokenSet) 
    - [x] add test to render existing built-in user
    - [x] add tests to check encoding/decoding of user permissions
    - [x] certain views and/or types need admin/config permission to edit or list or view
    - [x] list description for user
    - [x] annalist-manager updates to initialize site-users directory, but don't wipe existing user permissions
    - [x] annalist-manager option to update existing Django user to admin status
    - [x] annalist-manager option to create site user entry and default site permissions
    - [x] what site-level permission is required to create new collection?
        - Site-level CREATE/DELETE.  
        - Add test cases
    - [x] annalist-manager option to delete existing user
    - [x] site-wide permissions (e.g. to create collections) need to be site permissions
    - [x] implement delete user handler and tests - WONTDO: handled by generic entity delete
- [x] Default button on view edit form (and others) should be "Save".
    - See http://stackoverflow.com/questions/1963245/.
    - I found adding a duplicate hidden save button at the top of the <form> element did the trick.
- [x] List view: option to hide columns on smaller screens (cf. permissions)
- [x] Additional test cases [#8](https://github.com/gklyne/annalist/issues/8)
    - [x] Missing resource error reporting in:
        - [x] annalist/views/collection.py (missing collection)
        - [x] annalist/views/recordtype.py (missing type)
        - [x] annalist/views/genericlist.py (missing collection, type, list description)
        - [x] annalist/views/genericedit.py (missing collection, type, view description, entity)
- [x] Scan code for all uses of 'annal:xxx' CURIES, and replace with ANNAL.CURIE.xxx references.  (See issue [#4](https://github.com/gklyne/annalist/issues/4))
- [x] Add field to view: check property URI is unique
- [x] Don't store host name in entity URL fields (this is just a start - see issues [#4](https://github.com/gklyne/annalist/issues/4), [#32](https://github.com/gklyne/annalist/issues/32))
- [x] Investigate use of path-only references for copntinuation URIs
    - [x] would need to resolve when generating Location: header field ...
    - It turns out that instances of continuation URI with hostname are all used for testing Location: header responses, hence there's nothing to do (except add a few comments).
- [x] set base directory for running tests so that annalist_root doesn't appear in test names
    - tried, but doesn't seem to be an easy way to do this (apart, maybe, from creating a new test runner)
- [x] Initial documentation of authorization controls
- [x] Review getting started documentation in light of new authz controls
- [x] Flesh out the user documentation
- [x] record new demo screencasts
- [x] Seems to be a problem renaming a type for which there are defined values: need to rename the typedata directory too.  See Issue [#34](https://github.com/gklyne/annalist/issues/34)
- [x] Create new type: leave type URI field blank.
- [x] BUG: if default list description is deleted, collection cannot display.  Should revert to default default? [#36](https://github.com/gklyne/annalist/issues/36)
- [x] BUG: deleting type with existing records causes Server Error 500.  [#34](https://github.com/gklyne/annalist/issues/34)
- [x] Clean out old code, especially check @@TODOs in `entityedit.save_entity`
- [x] Test creation of cruising log (again) using real log data
    - [x] BUG: place name links to daily log record, not place record [#37](https://github.com/gklyne/annalist/issues/37)
    - [x] Provide option for optional enumerated value in field definitions (Enum_optional per render_utils)
- [x] Use separate Django database for each configuration
- [x] Think about how to handle change of email address (option to remove user from Django database?)
    - annalist_manager now has deleteuser option
- [x] Include date+time in log entries


## Version 0.1.4

Cleaning up some simple bugs and presentation problems.

From here on, use convention of even numbers for stable sub-releases and odd numbers for working versions.

* Post-release documentation updates
* Update annalist_manager with updatesitedata command and to create auth providers directory
* Updated field view definition to include extra fields used for enumerated type displays, etc.
* Updated view editing form description.
* Update field and view description of fields to restrict presentation of field choices
* Fix problem of ignoring blank value in submitted form (issue #30)
* Use collection and list labels for headings on entity list page (issue #26)
* Clean up page and section headings in record editing view
* Change confusing 'Select' label of field id (Field_sel) dropdown in view description
* Initialize entity label and comment to blank (issue #24)
* Fixed problem with rename locally created Default_view (issue #22)
* Fix that changing type of entity was not deleting old record (issue #29)

### TODOs completed for 0.1.4

- [x] annalist-manager option to update site data, leaving the rest untouched
- [x] annalist-manager initialize: needs to create `.annalist/providers` directory [#27](https://github.com/gklyne/annalist/issues/27).
- [x] Update view and field descriptions [#16](https://github.com/gklyne/annalist/issues/16)
    - [x] extend field edit form to include additional fields used.
    - [x] extend view edit form to include additional fields used in sitedata (i.e. record_type)
    - [x] add more 'annal:field_entity_type' constraints for fields that are intended to be used only with specific entity types (e.g. fields, views, etc.)
    - [x] List view also needs 'annal:field_entity_type' to control selection
        - [x] Add field manually to internal list descriptions
        - [x] Add field to List_view
    - [x] Remove "Default_field"
- [x] Blank value in submitted form is ignored [#30](https://github.com/gklyne/annalist/issues/30)
- [x] List headings are clutter [#26](https://github.com/gklyne/annalist/issues/26)
- [x] Clean up page and section headings in record editing view
- [x] 'Select' label for field type is un-obvious [#25](https://github.com/gklyne/annalist/issues/25)
- [x] New entities are initially populated with useless junk [#24](https://github.com/gklyne/annalist/issues/24)
    - initialization logic is in models.entitytypeinfo.get_initial_entity_values
- [x] Change type of entry doesn't delete old record [#29](https://github.com/gklyne/annalist/issues/29)
    - [x] Fix bug in entityedit (not usinjg new type info to check existence of renamed entity)
    - [x] Fixed gaps and bug in test code
- [x] Can't rename locally created Default_view [#22](https://github.com/gklyne/annalist/issues/22)
    - [x] Fix up default action resulting from click on link may need to change later when read only views introduced
    - [x] Additional authorization check if Save called with unexpected action
    - [x] Update authorization reporting to say what access (scope) was requested, rather than HTTP method

## Version 0.1.3

* First public prototype release

## Version 0.1.2

* Test with Django 1.7
* Initial installation kit
* Apply sorting to entity lists to make test cases more robust across systems
* Setup scripts to initialize installation and site data
* Fix problem with local logins
* Various minor page presentation changes
* Access root URI path ('/') redirects to site display
* Add some online help text for site, collection front pages, and login page
* Resolve virtualenv problem on Ubuntu 14.04
* util.removetree hack to allow test suite to run on Windows
* Initial documentation
* Demonstration screencast

## Version 0.1.1

* Feature freeze
* See below for summary of history to this point

## Initial public prototype outline plan

Initially guided by mockups per https://github.com/gklyne/annalist/blob/master/documents/mockup/Annalist.pdf?raw=true

1.  Front page/initial display
    * [x] form elements to create new collection
    * [x] form elements to delete collection
    * [x] include supporting logic in Collection module
    * [x] rework authentication/authorization to allow unauthenticated access for public data 
    * [x] test cases for site, site views; refactor tests to separate directory, modules
    * [x] adopt responsive CSS framework (Foundation)
2.  Collection display
    * [x] refactor metadata field access to common superclass
    * [x] types
        * [x] implement skeleton RecordType module
        * [x] create test cases for types in collection
        * [x] implement type methods
    * [x] views
        * [x] implement skeleton RecordView module
        * [x] create test cases for views in collection
        * [x] implement view methods
    * [x] lists
        * [x] implement skeleton RecordList module
        * [x] create test cases for lists in collection
        * [x] implement list methods
    * [x] UI test cases
    * [x] form elements to add/delete types/views/lists/...
    * [x] Add CollectionActionView test cases (handled with entity managed)
3. Record type display
    * [x] template
    * [x] view: edit form display
    * [x] view test cases
    * [x] refactor redirect_info, redirect_error in generic view to takle URI rather than view name parameter, and add new method to handle URI generation from view name + params.
    * [x] model
    * [x] model test cases
    * [x] view edit form response handling
    * [x] refactor code locally
    * [x] more refactoring; try to abstract common logic for RecordList, RecordView
    * [x] review generic view base functions - should some be inlined now?
    * [x] Move types/views/lists data into _annalist_collection directory
4. Default record view/edit display (code to be refactored later)
    * [x] form generation
    * [x] form display test cases
    * [x] provision for data access fallback to site data (for types, views, fields, etc.)
    * [x] form response handler
    * [x] test cases
    * [x] refactor URI and test data support for test cases to separate module; use reverse for URI generation; 
    * [x] refactor DefaultEdit form display
    - [x] WONTDO: isolate directory generation for tests.
    * [x] change <site>/collections/ to <site>/c/ or <site>/coll/ throughout.
    - [x] WONTDO: Similar for /d/ and /data/?
    * [x] include path values in entities.
    - [x] WONTDO: include base and reference values in entities. (later: requires use of @context)
    * [x] create data view display based on generic render logic
    * [x] editing recordtype: returns "already exists" error; display operation (new, copy, edit, etc) in edit form
    * [x] function to create initial development site data (based on test code)
    - [x] WONTDO: entity should carry its own RecordType id (where it's kept within a collection).  Have implemented alternative mechanism through bound_field that allows the entity to be less self-aware, hence more easily ported.
    * [x] menu dropdown on small display not working: need JS from Zurb site? (fixed by update to 5.2.1)
5. Default record list display
    * [x] form generation
    * [x] form display test cases (initial for default and all)
    * [x] include sitedata lists in drop-down
    * [x] form response handler (delete and others todo)
    * [x] entity list view: add selection fields (and classes)
    * [x] form response test cases
    * [x] customize response handler
    * [x] new entity from list-all display; changing type of entity
        * [x] Create default type in site data
        * [x] Create field render type for drop-down (render_utils and field template)
        * [x] Add field to default display
        * [x] Add type list data to display context
        * [x] Add original type as hidden field in edit form
        * [x] Add logic to form submission handler
        * [x] add test cases for changing type id (new and edit)
        - [x] WONTDO: remove recordtypedata access from entityeditbase.get_coll_type_data to POST handler (for recordtype, etc., the collection object is supplied as parent, so this is not so simple.)
        * [x] remove return_value from field definitions - this is now handled differently
        * [x] new record from list all: use default type, not random selection
        * [x] new record, change type, error doesn't redisplay types
        * [x] error loses continuation URI in edit form
        * [x] remove message header that appears on return from form edit (appears to be resolved?)
        * [x] review skipped tests - can any be enabled now?
        * [x] delete entity continues to wrong page
    * [x] add entity links to list views
        * [x] Update bound_field to provide access to entity URI
        * [x] Create field render type for entity ref
        * [x] Update field in default list displays
    * [x] connect site display to default display of entities, not customize
    * [x] connect list display to record view display
    * [x] build entity selector logic into list view
6. Generic entity edit view
    * [x] extract/generalize relevant logic from `defaultedit.py`
    * [x] parameterize view-id on extra URI field
    * [x] create new URI mapping entries
    * [x] create new test suite for generic edit view
    * [x] refactor defaultedit.py as special case (subclass?)
    * [x] fix urls.py error and re-test
7. Generic record list display and editing
    * [x] extract/generalize relevant logic from `defaultlist.py`
    * [x] refactor defaultlist.py as special case (subclass?)
    * [x] parameterize view-id on extra URI field
    * [x] create new URI mapping entries
    * [x] create new test suite for generic list view
        * [x] choose test scenario: Field definitions: http://localhost:8000/annalist/c/coll1/d/_field/ 
        * [x] list field descriptions?  Need to create list description (4 fields?).  http://localhost:8000/annalist/c/coll1/l/Fields_list/_field/
        * [x] also choose / define default view for list (Create field view?)
        * [x] need to rationalize entity display structure to encompass data, collection level metadata and site-level metadata.
        * [x] check list display in dev app
        * [x] define test suite test_genericentitylist based loosely on test_entitydefaultlist
        * [x] create test case for creating/editing site metadata entities (currently fail in dev system) e.g. create test_entitymetadataedit based on entitygenericedit.
        * [x] create edit view tests for all the main entity classes (type, view, list, data), along the lines of test_entityfieldedit, moving support code out of entity_testutils.
            * [x] copy/refactor test_recordtype to use same pattern as test_entityfieldedit
            * [x] see if old record type view class can be deleted
            * [x] incorporate model tests in test_entityfieldedit (cf. test_recordtype)
            * [x] rename test_entityfieldedit -> test_recordfield? (cf. test_recordtype)
        * [x] resolve overloading of "entity_uri" in context.
    * [x] entity_uri appears in entity view context as name (same as annal:uri) but also in bound field as locator.  Change name used in bound field to `entity_ref`.
    * [x] refactor delete confirm code to generic module, with type-specific messages.  Note that type, view and list deletes are triggered from the collection edit view, with different form variables, and also have specific remove functions in the collection class, so need separate implementations (for now?).
    * [x] update render template/logic for RecordView_view
    * [x] update template to include delete field options; finalize form response data
    * [x] implement tests for add/delete fields
    * [x] implement handlers for add/delete fields
    * [x] edit form response should update, not replace, any data from the original (so data from multiple views is not discarded).
    * [x] implement delete confirm view for views and lists.
    * [x] review missing tests: implement or delete?
    * [x] fix up view links from list display
    * [x] define View-list and List-list
    * [x] view button handler from list display + test
    * [x] continuation handling: replace by more generic parameter handling based on dictionary; move handling of escape logic, etc.
    * [x] search button handler from list display
    * [x] consider that 'Find' and 'View' buttons could be combined
    * [x] don't include continuation-uri param when URI is blank
    * [x] implement some version of entity selection logic
    * [x] decide how to handle presentation of field types (where?): (a) use simple text string, not CURIE; (b) use CURIE, but use render type to extract ID; but will need to map back when form is submitted?
        * [x] it all rather depends on the anticipated extensibility model for field types.  Option (a) is simplest for now.
    * [x] default_view response handler (needs generic view to make sense)
    * [x] implement view- and list- edit from collection customization page
    * [x] implement per-type default list and view
        * [x] already works for list view; e.g. http://localhost:8000/annalist/c/coll1/d/_type/
        * [x] but not yet for entity view; e.g. http://localhost:8000/annalist/c/coll1/d/_type/type1/
        * [x] return list_info structure rather than saving values in object. 
    * [x] consider replicating list_seup logic for view_setup.
    * [x] find and eliminate other references to get_coll_data, etc.
    * [x] don't return placeholder text in a form as field value; use HTML5 placeholder attribute
    * [x] refactor fields package as subpackage of views
    * [x] fix entity links to use default view URI (/d/...)
    * [x] List type + "View" selection uses // for type field - select based on list or suppress
    * [x] customize > edit record view > add field > cancel -- returns to wrong place.
    * [x] need test case for remove field with no field selected
    * [x] factor out add-field logic used by current add-field code
    * [x] test case for POST with 'add_view_field'
    * [x] provide option to invoke add-field logic during initial form rendering
    * [x] add_field button on entity edit displays; need way to control its inclusion
    * [x] new entity initialization vector through typeinfo, AND/OR provide mechanism to associate initial values for each entity type.
    * [x] "Add field" when creating new entity results in multiple entities created (use !edit for continuation URI?)  Add test case.
    * [x] tests
        * [x] skipped '@@TODO defaultlist default-view button handler'
        * [x] skipped '@@TODO defaultlist search button handler'
        * [x] skipped '@@TODO genericlist default-view button handler'
        * [x] skipped '@@TODO genericlist search button handler'
            * [x] annalist.tests.test_entitygenericlist.EntityGenericListViewTest
        * [x] skipped '@@TODO genericlist default list button'
            * [x] annalist.tests.test_entitygenericlist.EntityGenericListViewTest
8. initial application testing
    * [x] review and simplify bound_field logic for accessing field_value
    * [x] Create new type - appears twice in default_list_all display.  Delete one deletes both appearances, so this looks like display problem.  I thought this had been fixed.  Confirmed to be knock-on from incorrect creation of _type data (see next).
    * [x] New entry save as _type does not create new type in collection
    * [x] field view has size/position field; use as default when adding to view.
    * [x] viewing new entity with custom type generates "keyerror annal:value_type" @ fielddescription.py line 55.
    * [x] update field view description to display all relevant fields; ???
    * [x] when defining a field, the render type selected also implies a field value type; handle this in "FieldDescription constructor?"  Later, maybe.  For now, add value type field.
    * [x] make FieldDescription constructor more resilient to missing data.
    * [x] Changing type to built-in type in entity edit display does not save to correct location
    * [x] List editing view formatting is messed up (small-6?)
    * [x] Click on local type in default_list, then cancel, returns to Type_list display.  No continuation_uri in links.
    * [x] Click on local record in Default_list, cancel, returns to default data display (/d/ rather than /l/).  In default display, types don't appear.
    * [x] grey out set_default button on collection default display (/d/, /l/)
    * [x] When creating new collection, there's no obvious way to create a new record type (or view).
    * [x] Handle bare /l/ URI and redirect to default view for collection
    * [x] Remove precalculated list_ids and view_ids from view context
    * [x] Script to refresh sitedata in devel site
    * [x] In view editing, provide field id drodown
    * [x] In list displays, hyperlink entity type to view/edit form
    * [x] No easy way to create field description while editing view details; include new-field button
        * [x] update form template
        * [x] implement handler for 'new_field' response
        * [x] implement test case for 'new_field' response
        * [x] list description view not showing types or views in dropdowns
        * [x] introduce Default_field type
    * [x] When defining field, missing placement is silently ignored; field is not saved; (still)
    * [x] Authorization of field editing is not handled consistently:  allows config when no delete authz (no login)
    * [x] Display of remove-field checkbox based on "delete" permission. 
    * [x] Save entity edit is not requiring login - should check from POST?
    * [x] Entityedit add test cases for unauthorized config requests (and more?)
    * [x] From type display, want easy retreat to default display for collection
    * [x] View_type display should suppress add-field option.  Similar for View_list and View_field?
    * [x] suppress _initial_values as option when selecting type/view/list
    - [x] WONTDO: Add field allows new view type to be created, but how to make this default for displayed type?
    * [x] Generic field renderer for entityref as selection among available entity ids.  Use for field selection.  Options should be reworked using this form of enumeration, handled on the fly as required, using type information from the field definition.
    * [x] Type view should have dropdowns for default view and list
    * [x] List view selector syntax isn't working: need to nail down how type selection can work.  In saved data, I'm seeing '"annal:type": "annal:EntityData"', which isn't realy helpful.
        * [x] change all references to annal:type to @type, in sitedata and code (i.e. URIs/CURIE values).  E.g. annal:Type, annal:View, annal:EntityData, etc.
        * [x] for annal:type, assign local type_id value.  Consider renaming as annal:type_id.
        * [x] annal:type is retained for URI/CURIE of entity class (is this helpful?)
        * [x] list type selectors then use local type_id values.
    - [x] WONTDO: @type list selector - allow selection by type substring - e.g. coll/type
    * [x] When not logged in, should still have option to select a different view
    * [x] From list view, continuation URI for new, copy, etc should exclude message parameters.  In particular, links in rendered fields have the extra stuff.  (But do include ?search param)
    * [x] Customize > delete record > confirm : returns to wrong place
    * [x] Generalized enumeration types
        * [x] Define new RecordEnum class with type_id parameter on constructor; dynamically created directory paths; dynamic class creation?
        * [x] Test cases for RecordEnum
        - [x] WONTDO: Add optional type_id to all entity constructors (ignore on existing)
        * [x] Update entitytypeinfo to support enum types
        * [x] More test cases?
        * [x] Review, rationalize type naming and type ids.  Update sitedata.
        * [x] Update list type field definition
        * [x] Update tests using list type field definition
        * [x] Create type records for enumeration types, used for:
            - locating the default view and/or list id for records of that type
            - getting entity @type URI/CURIE values while editing
            - getting a view/edit link to type record
            - See notes in models.typeinfo
    * [x] Enumeration type for list types (list/grid: default list)
        * [x] Update field definition
        * [x] Create type record
        * [x] Update/add tests cases
    * [x] Enumeration type for field render types (text, testarea, etc...); use in fields display
        * [x] Create enumeration data
        * [x] Update field definition
        * [x] Create type records
        * [x] Update/add tests cases
        * [x] development test site is broken - why?  Isolate problem in test before fixing.
    * [x] allow '//' comments in JSON files - strip out before parsing JSON (but leave blank lines)
    * [x] Don't show Bib_* fields for non-biblio record types 
        - [x] WONTDO: Move Bib_* fields to separate "built-in" collection
        - [x] WONTDO: Can enumeration-like logic be used to support sub-areas in site data?
        * Long term is to move Bib_ field types out of site data, and provide easy way to incorporate library fragments into new collections, but for now they are part of the test environment.  See below.
        * Alternative might be value-scoped enumerations
        * [x] Update EntityFinder logic to support tests comparing with enclosing view fields
        * [x] Update entity selector call site (just one)
        * [x] Update selector syntax and sitedata
        * [x] Use EntityFinder logic in enumeration selection (FieldDescription.py)
        * [x] Add view context to FieldDescription
        * [x] Introduce biblio record type
        * [x] Introduce biblio record list
        * [x] Update test cases
        * [x] Field name updates (field_render, value_type)
        * [x] Update test cases
        * [x] Add fields to restrict bib_* fields to BibEntry views
            - [x] WONTDO: Declare additional/multiple types for entity?
        * [x] Update field selector view
        * [x] Use field selector in FieldDescription
        * [x] Update test cases
9. Prepare for release 0.1
    * [x] feature freeze
    * [x] version identifier in system
    * [x] remove dead code
    * [x] test with Django 1.7
    * [x] installation package
    * [x] test installation on non-development system
        * [x] sorting of enumeration lists
        * [x] sorting of entity lists (by typeid then entityid)
        * [x] sorting of entity lists enumerated in tests
        * There could be more test cases that need hardening, but so far all pass on a Linux deployment
    * [x] check python version in setup
    * [x] __init__.py in annalist_root dir causes test failure on Ubuntu 14.04; cf. https://code.djangoproject.com/ticket/22280.   Removing it solves the test case problem, but it was included originally to get the setup.py script to work as intended.  Try removing it and see if we can get kit builder to work.
    * [x] Login page - link to local Django login & admin pages
    * [x] Fix profile display with local credentials
    * [x] Logged-in username should appear in top menu; e.g. xxxx profile or xxxx: profile logout
    * [x] root URI - redirect to /annalist/site/
    * [x] utility/script for running tests
    * [x] utility/script for site creation
    * [x] utility/script for running server
    * [x] online help text (initial)
    - [x] WONTDO: Test installation on Windows (De-prioritized for now. Tests pass, but having problems accessing the settings when running the server. Change directory?)
    * [x] Documentation
        * [x] release notes/introduction;  link from README (about this release); key missing features/issues
        * [x] installation - link from README
        * [x] getting started - reference installation then walk through demo sequence; link from README (getting started);
        - [>] demo script (needs cleaning up)
        * [x] using Annalist - flesh out; link from README
        * [x] flesh out introduction/overview
        * [x] how to setup OpenIDConnect providers - move to separate document; link from installation doc
        * [x] tidy up README
        * [x] Move remaining TODOs to Roadmap and issues
        * [x] Flesh out roadmap
    * [x] Create mailing list -- see https://groups.google.com/forum/#!forum/annalist-discuss
    - [>] Demo deployment
    * [x] Demo screencast -- see http://annalist.net
    - [x] Add TODO list to release notes, and reset
    - [x] Bump version and update history
    - [x] Update version number in scripts, documents, etc.
    - [x] Post updated kit download
    - [x] Update front page link at annalist.net
    - [x] Upload to PyPI
    - [x] Final updates to master
    - [x] Post announcement to Google Group, and elsewhere

