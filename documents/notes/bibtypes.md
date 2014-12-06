# Bib types

(Details copied from http://en.wikipedia.org/wiki/BibTeX for ease of reference)

## article

An article from a journal or magazine.

Required fields: author, title, journal, year

Optional fields: volume, number, pages, month, note, key

## book

A book with an explicit publisher.

Required fields: author/editor, title, publisher, year

Optional fields: volume/number, series, address, edition, month, note, key

## booklet

A work that is printed and bound, but without a named publisher or sponsoring institution.

Required fields: title

Optional fields: author, howpublished, address, month, year, note, key

## inbook

A part of a book, usually untitled. May be a chapter (or section, etc.) and/or a range of pages.

Required fields: author/editor, title, chapter/pages, publisher, year

Optional fields: volume/number, series, type, address, edition, month, note, key

## incollection

A part of a book having its own title.

Required fields: author, title, booktitle, publisher, year

Optional fields: editor, volume/number, series, type, chapter, pages, address, edition, month, note, key

## inproceedings

An article in a conference proceedings.

Required fields: author, title, booktitle, year

Optional fields: editor, volume/number, series, pages, address, month, organization, publisher, note, key

## manual

Technical documentation.

Required fields: title

Optional fields: author, organization, address, edition, month, year, note, key

## mastersthesis

A Master's thesis.

Required fields: author, title, school, year

Optional fields: type, address, month, note, key

## misc

For use when nothing else fits.

Required fields: none

Optional fields: author, title, howpublished, month, year, note, key

## phdthesis

A Ph.D. thesis.

Required fields: author, title, school, year

Optional fields: type, address, month, note, key

## proceedings

The proceedings of a conference.

Required fields: title, year

Optional fields: editor, volume/number, series, address, month, publisher, organization, note, key

## techreport

A report published by a school or other institution, usually numbered within a series.

Required fields: author, title, institution, year

Optional fields: type, number, address, month, note, key

## unpublished

A document having an author and title, but not formally published.

Required fields: author, title, note

Optional fields: month, year, key


# BibJSON structures

cf. http://okfnlabs.org/bibjson/

## Simple string fields

address: Publisher's address (usually just the city, but can be the full address for lesser-known publishers)

[annote: An annotation for annotated bibliography styles (not typical) @@ use rdfs:comment?

booktitle: The title of the book, if only part of it is being cited

chapter: The chapter number

edition: The edition of a book, long form (such as "First" or "Second")

editor: (see Bib_person_field_view below)

eprint: A specification of an electronic publication, often a preprint or a technical report @@handle as identifier/link?

howpublished: How it was published, if the publishing method is nonstandard

institution: The institution that was involved in the publishing, but not necessarily the publisher

journal: (see Bib_journal_field_view below)

[key: A hidden field used for specifying or overriding the alphabetical order of entries (when the "author" and "editor" fields are missing).]

month: The month of publication (or, if unpublished, the month of creation)

[note: Miscellaneous extra information @@ use rdfs:comment?]

number: The "(issue) number" of a journal, magazine, or tech-report, if applicable. (Most 
publications have a "volume", but no "number" field.)

organization: The conference sponsor

pages: Page numbers, separated either by commas or double-hyphens.

publisher: The publisher's name

school: The school where the thesis was written

series: The series of books the book was published in (e.g. "The Hardy Boys" or "Lecture Notes in Computer Science") @@ field missing

title: The title of the work

type: The field overriding the default type of publication (e.g. "Research Note" for techreport, "{PhD} dissertation" for phdthesis, "Section" for inbook/incollection)

volume: The volume of a journal or multi-volume book

year: The year of publication (or, if unpublished, the year of creation)


## Object fields

### Bib_person_field_view

author: [list] The name(s) of the author(s)
editor: [list] The name(s) of the editor(s)

    id:
    name:
    alternate:
    firstname:
    lastname:


### Bib_journal_field_view

journal: [object] The journal or magazine the work was published in
    id:
    name:
    shortcode:


### Bib_license_field_view

license is a list of objects
license:
    type:
    url:
    description:
    jurisdiction:


### Bib_identifier_field_view

identifier is a list of objects
identifier:
    id:
    type: (e.g. DOI, crossref,)
    url:
    anchor:

