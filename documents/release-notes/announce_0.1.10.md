To Google group:

I've just released an update (0.1.10) to the public prototype of Annalist.

The main new features are usability enhancements, particularly in the possible workflows for creating linked records; support for property aliasing; simplified interface for viewing entity lists; and some presentation improvements.

This release is additionally available as a Docker comntainer from DockerHub (see quick staret and installation instructions.)

Summary of improvements and bug-fixes:

* Option to create new linked record from referring record view.  This means, for example, when creating a view description that the field selector drop-downs have an additional "+" button that can be used to create a new field type definition.  This feature is provided for all enumerated value fields that refer to some other entity type.
* Add field alias option.  This allows record-specific fields to be returned as the value for some other property URI;  e.g. in bibliographic records (`BibEntry_type`), the `bib:title` field can be used for `rdfs:label` values, and hence appear in views that expect `rdfs:label` to be defined.
* When changing a list view, don't filter by entity type.  Previously, when listinging (say) all `_type` entities, and changing the list type to `View_list`, no entries would be displayed because of conflicting entity selection criteria.
* Use more obvious interface for displaying collection only vs collection+site entity listings.  Previously used an explicit type id in the URI to display collection+site data; now uses `View` vs `View all` buttons to display collection-only or collection+site data respectively.
* Rework handling of repeated use of same field.  In previous releases, having the same field type appear more than once in a view description could lead to unexpected happenings when editing an entity.  This is now fixed by ensuring that a unique property URI is used for each one.
* `annalist-manager` enhancements; permissions help, new information subcommands
* Various form presentation improvements and bug fixes.

More details can be found in the "History" section of the [release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md), and via the GitHub issues list.

#g

...

To research-object:

I've just released Annalist 0.1.10.

The main new features are usability enhancements, particularly in the possible workflows for creating linked records; support for property aliasing; simplified interface for viewing entity lists; and some presentation improvements.

This release is additionally available as a Docker comntainer from DockerHub (see quick staret and installation instructions.)

The full announcement is at:
...

Release notes (see "history" section for details) at:
...

Annalist project on Github:
https://github.com/gklyne/annalist

Live demonstrator:
http://annalist.net/ and http://demo.annalist.net/

#g
--
