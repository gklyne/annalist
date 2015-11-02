## To Google group:

### Announcing Annalist release 0.1.22

I've just released an update (0.1.22) to the public prototype of Annalist.  

This release puts "linked data" in the Annalist linked data notebook.  Up to this point, Annalist data has been stored and indirectly accessible as JSON, with Compact URI strings (CURIEs) used as key values for attributes.  This release augments the JSON data with auto-generated JSON-LD context files so that the JSON data can be read and processed as [JSON-LD](http://json-ld.org/#).

The web pages for Annalist records now return links to the underlying JSON-LD data:

1. as "get the data" clickable links in the web pages,
2. as HTML `<link>` elements (with `rel=alternate` and content type attribute) in the web page header, and
3. as HTTP `Link:` headers (also with `rel=alternate` and content type attributes).

(Not implemented in this release, but intended for a future release, is HTTP content negotiation available on the primary URI for each entity record.)

Some bugs have been fixed, as noted in the version 0.1.21 summary.

More details can be found in the "History" section of the [release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md), and via the GitHub issues list.

As always, the live demo system is at [demo.annalist.net](http://demo.annalist.net/annalist/site/), and [instructions for installing Annalist](https://github.com/gklyne/annalist/blob/master/documents/installing-annalist.md) are available from, the [Annalist GitHub project](https://github.com/gklyne/annalist).  The [Annalist tutorial](http://annalist.net/documents/tutorial/annalist-tutorial.html) is also available from the demo system site.

#g

...

## To research-object, RDS-CREAM and FAST:

### Announcing Annalist release 0.1.22

I've just released Annalist 0.1.22.

This release puts "linked data" in the Annalist linked data notebook, with support for access to Annalist data records as [JSON-LD](http://json-ld.org/#).

The full announcement is at: 
https://groups.google.com/d/msg/annalist-discuss/....

Release notes (see "history" section for details) at:
https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md

Annalist project on Github:
https://github.com/gklyne/annalist

Live demonstrator:
http://annalist.net/ and http://demo.annalist.net/

Online tutorial document (draft, work-in-progress):
http://annalist.net/documents/tutorial/annalist-tutorial.html

#g

...

