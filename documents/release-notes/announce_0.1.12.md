To Google group:

I've just released an update (0.1.12) to the public prototype of Annalist.

New in this release are non-editing entity views, with links to referenced entities.  This facilitates navigation of the network of entities that make up a collection.  A number of new render types have been introduced, many to support more useful data display in the non-editing view (links, Markdown formatting, etc - more details below.).  This non-editing view is now the default used when viewing an entity (e.g. when following a link from a list view).

The changes can be seen by browsing to http://demo.annalist.net/annalist/c/DMO_Experiment/d/, and clicking around from there.

This release also contains a number of usability enhancements and bug fixes, including:

* Saves server logs in root of annalist_site data, for Docker visibility.  When Annalist is running in a Docker conainer, another container can attach to the same data data volume in order to view the server logs (see the [installation instructions](https://github.com/gklyne/annalist/blob/master/documents/installing-annalist.md) for more information about how to do this).
* New render types: Boolean as checkbox, URI as Hyperlink, URI as embedded image, long text with Markdown formatting.
* New CSS styles for formatting Markdown text.
* Page layout/styling changes; rationalize some CSS usage to achieve greater consistency between the editing, non-edit and list views.
* Change 'Add field' button to 'Edit view' - this switches to the view editing page where field definitions can be changed, added or removed.
* Add 'View description' button on non-editing entity views - this switches to a display of the view description.  Subject to permissions, an 'Edit' button allows the view definition to be edited.
* View display: suppress headings for empty repeatgrouprow value.
* Preserve current value in form if not present in drop-down options.  This change ws introduced mainly to prevent some surprising effects when editing field descriptions; the change is partially effective, but there remain some link navigation issues when a field value of not one of those available in a drop-down selector.
* Various bug fixes

More details can be found in the "History" section of the [release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md), and via the GitHub issues list.

#g

...

To research-object:

I've just released Annalist 0.1.12.

New in this release are non-editing entity views, with links to referenced entities.  This facilitates navigation of the network of entities that make up a collection.  A number of new render types have been introduced, many to support more useful data display in the non-editing view (links, Markdown formatting, etc - more details below.).  This non-editing view is now the default used when viewing an entity (e.g. when following a link from a list view).

The changes can be seen by browsing to http://demo.annalist.net/annalist/c/DMO_Experiment/d/, and clicking around from there.

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
