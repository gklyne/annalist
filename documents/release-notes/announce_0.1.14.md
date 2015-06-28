To Google group:

I've just released an update (0.1.14) to the public prototype of Annalist.

New in this release is initial support for arbitrary binary attachments to Annalist entities, initially usable for adding image files to collections (previously, they must be published separately on the Web and referenced).

This release also contains a number of other enhancements and bug fixes, including:

* Add logic to serve content of attachment in orginally submitted form.
* Add "View" button to edit form.  This makes it possible to show hyperlinks that can be used to access referenced entities.
* Fix some situations causing "500 Server error" messages.
* Update continuation URI if necessary when an entity is renamed, to prevent some surprising "Entity does not exist" messages.
* Added software version to collection, and refuse access if collection version is higher than current software version.
* Don't save URL value in stored data; rather depend on its value being determined when an entity is accessed.  This potentially improves portability of data collections.
* Add documentation of view field descriptions, particularly to cover fields that are used to create entity attachments.
* Added internal support for complex field values that can be partially updated (used to support attachment metadata).
* Quite extensive code refactoring to support attachments.
* Added hooks for file format migration.

More details can be found in the "History" section of the [release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md), and via the GitHub issues list.

#g

...

To research-object:

I've just released Annalist 0.1.14.

The major new feature in this release is support for arbitrary binary attachments to Annalist entities, initially usable for including image files in collections (previously, they must be published separately on the Web and referenced).

The full announcement is at:
...https://groups.google.com/d/msg/annalist-discuss/lR4ADtfi10E/W75DnHLh9-sJ

Release notes (see "history" section for details) at:
https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md

Annalist project on Github:
https://github.com/gklyne/annalist

Live demonstrator:
http://annalist.net/ and http://demo.annalist.net/

#g
--
