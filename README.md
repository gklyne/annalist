annalist
========

Free-form web data platform - "Data management for little guys"

Goals
-----

* Easy data: out-of-box data acquisition and modification.
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data, with links in and links out.

Installation
------------

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

* Standard web server
* Access control with 3rd party IDP authentication
* Data storage model
    * File format RDF-based (JSON-LD?)
    * Records, Attachments, Collections, Groups
    * Directory structure
* User interface
    * Self-maintained configuration data
    * Grid-based flexible layout engine (e.g. Bootstrap)
* Bridges for other data sources
    * Spreadsheet
    * XML?
    * _others_

TODO
----

* Choose web server
* Authentication mechanism
* Access control model
* Define on-disk structure
    * Directories
    * Files
* Define data access API details
* Define UI generation details
* Implement data access API details
* Implement UI generation details
* Create core UI definitions
