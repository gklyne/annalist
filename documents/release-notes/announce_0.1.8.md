To Google group:

I've just released an update (0.1.8) to the public prototype of Annalist.

The main new feature in this release is full support for views containing repeated fields (e.g. a bibliographic entry containing multiple authors).  These can be displayed as a repeating group of fields formatted similarly to non-repeating fields (`RepeatGroup` render type) or as a repeating row of values with column headings (`RepeatGroupRow` render type).  With this enhancement, the core web presentation engine is substantially complete, with further capablities to be provided by adding new field renderers.

Summary of other improvements and bug-fixes:

- Added field groups as part of support for repeating fields in a data view.
- Updated sample descriptions of bibliographic data to use repeatinbg field groups, to fully support BibTeX/BibJSON-like structures.
- Update annalist.net demo site front page (see `documents/pages`).
- New test suite to check completeness and consistency of site-wide data.
- Fixed some bugs in field type selection when editing view descriptions.
- View generating code regorganization and rationalization.  Most of the HTML form-generating code is now in a separate code directory.
- Unification logic used to generate entity list displays and repeating fields in an entity view/edit form.
- Formatting, generated HTML and CSS changes; eliminate use of HTML `<table>`.
- Fix server error reported when copying view without URI field (also hotfix 0.1.6a).

More details can be found in the "History" section of the [release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md), and via the GitHub issues list.

#g

...

To research-object:

I've just released Annalist 0.1.8.  

This is the version I intend to demonstrate at FORCE2015 next month.

It is still a prototype release, with some important functions not completed, and usability improvements needed in some areas.  The main addition in this release is support for presentation of forms with repeating field groups (e.g. a bibliographic entry containing multiple authors).

The full announcement is at:
https://groups.google.com/forum/#!topic/annalist-discuss/JoDYIxzwPPI

Release notes (see "history" section for details) at:
https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md

Annalist project on Github:
https://github.com/gklyne/annalist

Live demonstrator:
http://annalist.net/ and http://demo.annalist.net/

#g
--
