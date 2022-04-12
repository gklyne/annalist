# Development roadmap

Current status: candidate feature-complete minimum viable product, release 0.5.18.

This is a maintenance release which drops support for Python 2, uses a recent version of Django (4.0.3), and applies security updates recommended by GitHub `dependabot`.


# V1.0 release

Outstanding issues leading up to V1.0 release are noted at [issues for V0.x alpha milestone](https://github.com/gklyne/annalist/milestones/V0.x%20alpha).

More generally, features planned for future releases are recorded in the [issues list](https://github.com/gklyne/annalist/issues).


# Desired features, not yet scheduled


## Data bridges

Especially spreadsheets.  See https://github.com/ninebynine/sds


## Web backend storage

(Moved to [issue #32](https://github.com/gklyne/annalist/issues/32))

(Also consider SoLiD, per discussion with TBL)


## Grid view

Alternative form of list view, e.g. for image galeries.


## Authentication

- OAuth2 dynamic registration - https://tools.ietf.org/html/rfc7591 - if IDPs support it.
- EUdat? (Also see notes from discussion at crossref with Matthew Dovey - cf The European Open Science Cloud for Research - EOSC - apparently this subsumes id aspects of EUDat.)


## Support multiple entity storage providers

This is an extension of the "Web backend storage" noted above.  An Annalist installation could be able to route entity access requests to different providers using different HTTP-based protocols (e.g. WebDav vs AtomPub), or other more specialized access mechanisms.


## Version management integration

1. Maintain collections as (say) git repositories with commit triggers.  (See also ROEVO work from Wf4Ever project).

2. Provide way to access historical versions (Memento?)

Notes:

- git integration for data versioning
- dat integration for versioning? (https://github.com/maxogden/dat)
- Memento integration for old data recovery


## Provenance and journalling

1. Capture provenance information as data records are updated (authenticated user, date+time, records view used, etc.)
2. Support provenance pingbacks, e.g. for discovery of downstream use.
    - Cf. [prov-aq/#provenance-pingback](http://www.w3.org/TR/prov-aq/#provenance-pingback)

Notes:

- provenance data capture (e.g. - look at creating additional resource in entity directory)
- provenance pingbacks - distributed provenance for real data?


## Ontology import and export

Create initial Annalist definitions from an imported Ontology.  These may not necessarily be the most effective presentation of data, but they can provide a starting point for refinement by hand.

Similarly, OWL and/or RDFS class and property declarations could be extracted and exported from definitions created with Annalist.  (There is already some logic in this direction used to create JSON-LD context files from Annalist definitions.)


## ResourceSync

Implement ResourceSync protocol for sharing and propagation of Annalist data sets.


## Deployment options

1. Debian package
2. Docker / DockerHub (done, but could be improved)
3. Look into using Vagrant and/or Puppet/Chef/...
4. Cloud appliance, etc.


# Other possibilities (not yet on roadmap)

- Checklist integration
- Shuffl integration?
- RML integration for data bridges

