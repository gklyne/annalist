# Development roadmap

@@TODO

# V1.0 release

@@TODO


# Desired features, not yet scheduled


## Web backend storage


## Linked data formats and API

namespaces

jsonld contexts

entity renaming and link preservation

alternate format renderers and content negotiation


## External references and local blob storage


## Extended data types and presentation options


## Grid view


## Collection templates


## Authorization and access control ramework


## Support multiple entity providers


## Version management integration

(Memento?)


## Provenance and journalling

(pingbacks)


## Data bridges

Especially spreadsheet.  See https://github.com/ninebynine/sds


## Research objects and checklists


## ResourceSync


## Deployment options

Cloud appliance, etc.


# Notes from original TODO

(These should be migrated to the headings above, or new roadmap headings.)

## Future features

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
- provenance data capture (e.g. - look at creating additional resource in entity directory)
- provenance pingbacks - distributed provenance for real data?
- git integration for data versioning
- dat integration for versioning? (https://github.com/maxogden/dat)
- Memento integration for old data recovery
- ResourceSync integration for data sync
- Shuffl integration?
- RML integration for data bridges

### Entity abstraction and storage

- replace/augment direct file access with HTTP access
- Note that it should be possible to take an Annalist site directory and dump it onto any regular HTTP server to publish the raw data.  Web site should still be able to work with that.
- think about storage of identifier URIs (e.g. record type URIs.)  Should they default to be:
  (1) relative to self
  (2) relative to base of site
  (3) relative to host
  (4) absolute
  (5) relative to base of collection
  Currently, it's (3) or (4), but I think I favour (2) (or (5)?).  The intent is that the URI field
  can be fixed by explicitly entering an absolute URI, but until then they are allocated
  per site.  The expectation is that if data are moved, it will be as complete collections
  to ensure they are accompanied by their associated metadata.  This is easiest with (5), but (2) may be easier to implement.
- see also notes below about URI/URL handling
- Note that entityroot.set_values currently favours a copy of the URL from the stored/internal data.  Currently this is created with a full URI (including hostname), but need not be.

### AnnalistGenericView:

- Generic renderers, all driven by a supplied dictionary:
  - HTML
  - JSON-LD
  - uri-list
- but serve native format directly.

### Deployment:
- look into using Vagrant and/or Puppet/Chef/... and/or docker

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
    * See https://github.com/gklyne/annalist/blob/develop/src/annalist_root/annalist/layout.py
    * @@NOTE: wean off direct directory access and use HTTP
* Define data access internal API details for web site
  * First cut in progress
  * @@NOTE: remember to use simple GET semantics where possible; may need to revisist and simplify
  * @@TODO: current implementation is file-based, but details are hidden in Entity classes.
* Define UI generation details
* Implement data access API details
  * Mostly straight HTTP GET, etc.  (Need to investigate access and event linkage - currently using direct file access for concept demonstrator.)




