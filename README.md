annalist
========

Free-form web data platform - "Data management for little guys"

Goals
-----

Think of a kind of "Linked data journal" or "Linked data wiki".  (The name "annalist" derives from ["a person who writes annals"](http://www.oxforddictionaries.com/definition/english/annalist).)

* Easy data: out-of-box data acquisition and modification
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data, with links in and links out.

Installation
------------

(Not final: these notes have been created as work-in-progress to capture anticipated dependencies)

    cd _workspase_base_
    git clone https://github.com/gklyne/annalist.git
    cd annalist

    virtualenv anenv
    pip install rdflib
    pip install rdflib-sparql
    pip install django
    pip install httplib2
    pip install oauth2client

Technical elements
------------------

Note: active development is taking place on the "develop" branch in git - see [https://github.com/gklyne/annalist/tree/develop]())

* Standard web server
* Access control with 3rd party IDP authentication
* File based data storage model
    * File format RDF-based. Have settled on JSON-LD for initial work.
    * Records/Entities, Attachments (blobs), Collections, Groups
    * Directory based organization
    * Separate indexing as and when required.
* User interface
    * Self-maintained configuration data
    * Grid-based flexible layout engine (e.g. Bootstrap)
* Bridges for other data sources
    * Spreadsheet
    * XML?
    * _others_

TODO
----

See: [https://github.com/gklyne/annalist/blob/develop/TODO.txt]()
