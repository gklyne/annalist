# Development roadmap

Current status: V0.1.3, first public protoype.


# V1.0 release

Outsatnding issues leading up to V1.0 release are noted at [issues for V0.x alpha milestone](https://github.com/gklyne/annalist/milestones/V0.x%20alpha).


# Desired features, not yet scheduled

## Web backend storage

The plan fopr Annalist has always been to separate the backend entity storage from the front en d user interface, thereby allowing hosting of data from the Annalist service.  Currently Annalist uses a file-based back-end which is not separately deployable.

Entity access has been isolated in a single module, so the effort required to replace file access with HTTP access should be modest once the design details have been worked out.

Notes:

- replace/augment direct file access with HTTP access
- Note that it should be possible to take an Annalist site directory and dump it onto any regular HTTP server to publish the raw data.  the Annalisrt web site should still be able to work with that.
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
- review URI structure and relation to file system layout
- need to address data access authorization (OpenID?), resource enumeration (WebDAV?), other issues
- Note that entityroot.set_values currently favours a copy of the URL from the stored/internal data.  Currently this is created with a full URI (including hostname), but need not be.
- need to address problem of getting HOST part of site URI when initializing a collection; can this logic be shifted to request code instead of __init__?


## Linked data formats and API

Currently, data is stored as JSON using JSON-LD elements and conventions (in particular property names, '@id' and '@type' fields). The intent is for Annalist data to be interpretable and presentable as RDF, which requires putting a number of additional elements in place:

Notes:

- namespaces and prefix URIs
- jsonld contexts
- alternate format renderers and content negotiation

There are also some issues around entity renaming and link preservation to be considered.


### Alternative formats to support

(cf. AnnalistGenericView)

- Generic renderers, all driven by a supplied entity data dictionary:
  - HTML
  - JSON-LD
  - uri-list
- but serve native format directly.


## External references and local blob storage

For example, to crerate galleries of annotated images.  Want easy capability to upload data and use the resulting URI as a link.


## Extended data types and presentation options

Numbers, Dates, Images, Georeferences, etc.

I also want to look into using "live" links, e.g. to obtain georeference coordinates or environment sensor data for incl,usion into data records.

Notes:

- more field types, including link browser
    - image grid + metadata pop-up for mobile browsing?


## Grid view

Alternative form of list view, e.g. for image galeries.


## Collection templates

Facilitate the creation of a new collection using the structures (data types, views, lists, etc.) from an existing collection.


## Authentication

- Alternative OIDC identity providers
- Authentication mechanisms
  - Consider using OAuth2-Shibboleth bridge for uni deployment (have link somewhere in notes)
- OAuth2 dynamic registration - note ongoing work in IETF (https://datatracker.ietf.org/doc/draft-ietf-oauth-dyn-reg/)


## Authorization and access control ramework

Curently authenticated users have full access.  Need to add a permission layer.

Notes:

- Assume use of Annalist form data under control of suitable authority
- Focus on form of authorization data
- Back-fit to form interface for creation of data; figure what seeding is needed
- Review proposed access control model
    - re-examine elements from UMA, see what can be used/is useful.


## Support multiple entity providers

This is an extension of the "Web backend storage" noted above.  An Annalist installation could be able to ropute entety access requests to different providers using different HTTP-based protocols (e.g. WebDav vs AtomPub), or other more specialized access mechanisms.


## Version management integration

1. Maintain collections as (say) git repositories with commit triggers.  (See also ROEVO work from Wf4Ever project).

2. Provide way to access historical versions (Memento?)

Notes:

- git integration for data versioning
- dat integration for versioning? (https://github.com/maxogden/dat)
- Memento integration for old data recovery


## Provenance and journalling

1. Capture provenance informnation as data records are updated (authenticated user, date+time, records view used, etc.)
2. Support provenance pingbacks, e.g. for discovery of downstream use.

Notes:

- provenance data capture (e.g. - look at creating additional resource in entity directory)
- provenance pingbacks - distributed provenance for real data?


## Data bridges

Especially spreadsheets.  See https://github.com/ninebynine/sds


## Research objects

Mechanisms for packaging to submitting to RO repositories.  Could be based on [DIP work](https://github.com/CottageLabs/dip), etc.


## ResourceSync

Implement ResourceSync protocol for sharing and propagation of Annalist data sets.


## Deployment options

1. Debian package

2. Docker

3. look into using Vagrant and/or Puppet/Chef/...

4. Cloud appliance, etc.


## Sample applications

* Cruising log
* Image database (bioimage revisited)



# Other possibilities (not yet on roadmap)

- Checklist integration
- Shuffl integration?
- RML integration for data bridges

