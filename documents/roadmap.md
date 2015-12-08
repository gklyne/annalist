# Development roadmap

Current status: public prototype release 0.1.24; this release introduces support for sharing structure definitions between collections.  This has been hotfix-patched as 0.1.24a to fix a test suite error.


# V1.0 release

Outstanding issues leading up to V1.0 release are noted at [issues for V0.x alpha milestone](https://github.com/gklyne/annalist/milestones/V0.x%20alpha).

More generally, features planned for future releases are recorded in the [issues list](https://github.com/gklyne/annalist/issues).


# Desired features, not yet scheduled


## Data bridges

Especially spreadsheets.  See https://github.com/ninebynine/sds


## Research objects

Mechanisms for packaging to submitting to RO repositories.  Could be based on [DIP work](https://github.com/CottageLabs/dip), etc.


## Web backend storage

(Moved to [issue #32](https://github.com/gklyne/annalist/issues/32))

(Also consider SoLiD, per discussion with TBL)


### Alternative formats to support

(cf. AnnalistGenericView)

- Generic renderers, all driven by a supplied entity data dictionary:
  - HTML
  - JSON-LD
  - uri-list
- but serve native format directly.


## Extended data types and presentation options

Numbers, Dates, Georeferences, etc.

I also want to look into using "live" links, e.g. to obtain georeference coordinates or environment sensor data for inclusion into data records.

Notes:

- more field types, including link browser
    - image grid + metadata pop-up for mobile browsing?
- see also: discussion with Cerys, and philosophy of minimal hurdles to data entry


## Grid view

Alternative form of list view, e.g. for image galeries.


## Authentication

- Alternative OIDC identity providers
- ORCID?
- Authentication mechanisms
  - Consider using OAuth2-Shibboleth bridge for uni deployment (have link somewhere in notes)
- OAuth2 dynamic registration - https://tools.ietf.org/html/rfc7591 - if IDPs support it.


## Support multiple entity providers

This is an extension of the "Web backend storage" noted above.  An Annalist installation could be able to route entety access requests to different providers using different HTTP-based protocols (e.g. WebDav vs AtomPub), or other more specialized access mechanisms.


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
    - Cf. [prov-aq/#provenance-pingback](http://www.w3.org/TR/prov-aq/#provenance-pingback)

Notes:

- provenance data capture (e.g. - look at creating additional resource in entity directory)
- provenance pingbacks - distributed provenance for real data?


## ResourceSync

Implement ResourceSync protocol for sharing and propagation of Annalist data sets.


## Deployment options

1. Debian package
2. Docker / DockerHub (done, but could be improved)
3. Look into using Vagrant and/or Puppet/Chef/...
4. Cloud appliance, etc.


## Sample applications

* Image database (bioimage revisited)


# Other possibilities (not yet on roadmap)

- Checklist integration
- Shuffl integration?
- RML integration for data bridges

