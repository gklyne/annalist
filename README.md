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

In Annalist, I hope to create a generic data journal which can be used for =diverse purposes, in which I have been motivated by the needs of small academic research groups, and my own past experiences running a small business.  I want to deliver is a self-hostable web-based tool that will, "out-of-box", allow collection of web accessible, linked data without prior design of its structure.  Rather, I want to allow structure in data to be developed as needs arise.  Some of my ideas for this are drawn from pre-web PC tools (e.g. [WordPerfect Notebook](https://raw.github.com/gklyne/annalist/master/presentations/wpnotebook_screenshots.png) and [Blackwell Idealist](https://raw.github.com/gklyne/annalist/master/presentations/matrix.png)) which used simple text based file formats to drive flexible, small-scale databases.  I find these products occupied a sweet spot that hasn't since been matched by any web-based software of which I'm aware.

The work on Annalist is in its very early stages, but I'm committed to open development from the outset, so you can see all the technical work and notes to date [here](https://github.com/gklyne/annalist).  There's nothing usable yet (as of January 2014).  Note that all the active development takes place on the ["develop" branch](https://github.com/gklyne/annalist/tree/develop).  In due course, I plan to follow a ["gitflow"-inspired](http://nvie.com/posts/a-successful-git-branching-model/) working style that uses the "master" branch for released, tested software.


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
