* see also: https://www.pivotaltracker.com/s/projects/781691

# Apache interface

http://httpd.apache.org/docs/2.4/mod/mod_actions.html - work with mod_wsgi??  Maybe fastCGI
http://code.google.com/p/modwsgi/ - "Daemon processes may if required also be run as a distinct user"

# Licencing

Publication licence, to be embedded in data created

Encourage CC0 or equivalent for anything made public-access.

Link rights information to access control?

# Data bridges

Read only - emphasis on using original tools for editing.

Expand architectural ideas:  plug-in via web service, etc.

Place in data collection path structure

# Applications

http://www.20thcpaint.org - interventions for conserving paintings.  Uses CIDOC-CRM++.  Could this be a model for Donna's ideas for recording and detecting stolen artworks?

# Other directions

IPython integration?
Annalist-driven presentation/notebook?
Mobile apps (or just web pages?)


# Comparison points:

- usable out-of-box for data collection
- setup/configuration by end user; incremental definition of structures
- semi-structured data - free text and "semantics"
- VCS-friendly (e.g. local data is also git repository); Dropbox-friendly; etc.
- mobile-friendly
- content accessible as linked data; links to/from public data
- desktop or web hosting; work with separately hosted data
- support external applications (REST API)
- open source

- usable out-of-box for data collection
- setup/configuration by end user
- semi-structured data
- data structure definable by "ordinary" user
- "broad data" support
- "source as resource"
- content accessible as linked data
- desktop or web hosting
- “Unhosted”-friendly (https://unhosted.org/), 
- Backup-friendly
- VCS-friendly (e.g. local data is also git repository), 
- Dropbox-friendly
- Curation Microservice friendly (https://confluence.ucop.edu/display/Curation/Microservice)
- links to/from public data
- search across all fields
- open source
- support external applications

# Related

* http://blog.okfn.org/2013/04/22/forget-big-data-small-data-is-the-real-revolution/
* http://oa.upm.es/15413/1/HERME_TCREP_ANDMANS_1998-3.pdf
* Filemaker comparison
* Check out Omni family (omnifocus?)
* Compare with http://meta.wikimedia.org/wiki/Wikidata/Notes/Inclusion_syntax
* Compare with http://www.researchspace.org/
  * CIDOC CRM based, information workbench based, CH-focus

## Comparison with Callimachus

* http://callimachusproject.org, http://code.google.com/p/callimachus/.

Looks very similar in concept - it appears that the big difference is "source as resource".

Apparently, very similar overall goals, but difference of style:
- C. not usable out-of-box for data collection
- C. requires understanding and editing of XHTML forms; I can't see lab researchers using this
- C. uses triple store rather than flat RDF storage; uses SPARQL as primary access/update mechanism???

## Comparison with Figshare:

Figshare is run by Digital Science, a division of Macmillan publishers.
Lead by Timo Hannay

Similar:
- arbitrary data
- API
- hosted (optional for Annalist)

Different:
- non-commercial base platform
- not centrally hosted
- open source
- arbitrarily structured data/metadata (can't tell what Figshare does)
- published as linked data (can't tell what Figshare does)
- integrated provenance(?)

My guess is that Annalist would be a potential platform for a system like Figshare,
but would require specific features added to replicate full functionality; i.e. occupies 
a different level in the stack.  The main difference in approach is that I'm focusing 
on locally installable (but web-connected) facilities for individuals and small groups.


# More links:

- http://homepages.inf.ed.ac.uk/opb/papers/PODS1997a.pdf (Buneman)
- http://cgi.csc.liv.ac.uk/~sazonov/papers/Paper393-Molyneux-Sazonov.pdf (Hyperset, Richard Molyneux, Vladimir Sazonov)
- http://senseidb.com
- http://infolab.stanford.edu/lore/pubs/lore97.pdf
- http://code.google.com/p/spinneret/ (last update 2009)
- http://stackoverflow.com/questions/227017/databases-which-can-handle-semi-structured-data (unimpressive responses, dated)
- http://figshare.com
- https://confluence.ucop.edu/display/Curation/Microservices
   - https://confluence.ucop.edu/display/Curation/CAN
   - https://confluence.ucop.edu/display/Curation/D-flat

- http://osbloggery.blogspot.co.uk/2007/12/after-idealist.html
- http://sourceforge.net/apps/mediawiki/qercus/index.php?title=Main_Page

- http://code.google.com/p/chromiumembedded/
- http://code.google.com/p/cefpython/



