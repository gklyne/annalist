## To Google group:

### Announcing Annalist release 0.1.24

I've just released an update (0.1.24) to the public prototype of Annalist.  

This release adds sharing of collection structure descriptions, which is a first step towards supporting modularization of data structure descriptions, which I'm hoping will help to make it easier to create customized collections.

An Annalist collection can be defined to inherit record type, view, list and other definitions from an existing collection.  This means a new collection can be created based on the structure of an existing collection, and then evolved as before.  Any changes that are made to the collection configuration are recorded in the new collection, and do not affect the original.

Also, a number of bugs have been fixed, and there has been some extensive internal code refactoring, in part to prepare the codebase for separation of record storage from the Annalist web service (e.g. to allow collections to be stored in separate Linked Data Platform servers).

More details can be found in the "History" section of the [release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md), and via the GitHub issues list.

The Annalist live demo system is at [demo.annalist.net](http://demo.annalist.net/annalist/site/), and [instructions for installing Annalist](https://github.com/gklyne/annalist/blob/master/documents/installing-annalist.md) are available from, the [Annalist GitHub project](https://github.com/gklyne/annalist).  The [Annalist tutorial](http://annalist.net/documents/tutorial/annalist-tutorial.html) is also available from the demo system site.

#g

...

## To research-object, RDS-CREAM and FAST:

### Announcing Annalist release 0.1.24

I've just released Annalist 0.1.24.  This release adds sharing of collection structure descriptions, which is a first step towards supporting modularization of data structure descriptions, and several bug fixes.

The full announcement is at: 
https://groups.google.com/d/msg/annalist-discuss/7lJN6ZzaISE/3Oq2ko-2CwAJ

Release notes (see "history" section for details) at:
https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md

Annalist project on Github:
https://github.com/gklyne/annalist

Live demonstrator:
http://annalist.net/ and http://demo.annalist.net/

Online tutorial document (draft, work-in-progress):
http://annalist.net/documents/tutorial/annalist-tutorial.html

#g


