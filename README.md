annalist
========

A free-form web data notebook - "Data management for little guys"

_Current status (2015-08-04):  public prototype, released for evaluation and feedback._ 

For information about the current release, please refer to the [V0.1 release notes](documents/release-notes/release-v0.1.md)


Quick-start
-----------

See [Getting started with Annalist](documents/getting-started.md).

There's also an [on-line demonstration server](http://demo.annalist.net/annalist/site/) - log in with a Gogle account to try creating or modifying data.


Installation
------------

See [Installing and setting up Annalist](documents/installing-annalist.md), and [Configuring Annalist to use OpenID Connect](documents/openid-connect-setup.md).


Using Annalist
--------------

See the [Guide to using Annalist](documents/using-annalist.adoc)

There are also a number of demonstration screencast videos, and accompanying scripts, which can be found at [demonstration/evaluation scripts](documents/demo-script.md) page.


Goals
-----

A _Linked Data Notebook_, supporting collection, organization and sharing of structured and semi-structured data.  The name "annalist" derives from ["a person who writes annals"](http://www.oxforddictionaries.com/definition/english/annalist).

* Easy data: out-of-box data acquisition, modification and organization of small data records.
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data, with links in and links out.

In Annalist, I hope to create a generic data notebook which can be used for diverse purposes, in which I have been motivated by the needs of small academic research groups, and my own past experiences running a small business.  I want to deliver a self-hostable, web-based tool that will, "out-of-box", allow collection of web accessible, linked data without prior design of its structure.  I aim to allow structure in data to be developed as needs arise.  Some of my ideas for this are drawn from pre-web PC tools (e.g. [WordPerfect Notebook](https://raw.github.com/gklyne/annalist/master/presentations/wpnotebook_screenshots.png) and [Blackwell Idealist](https://raw.github.com/gklyne/annalist/master/presentations/matrix.png)) which used simple text based file formats to drive flexible, small-scale databases.  I find these products occupied a sweet spot that hasn't since been matched by any web-based software of which I'm aware.

Annalist is a work-in-progress, but I'm committed to open development throughout, so you can see all the technical work and notes to date [here](https://github.com/gklyne/annalist).  It should be possible for a technically competent person to install and run the software, and get an indication of the direction I'm going.  Annalist software is available as source code from github, a Python installation package from PyPI, and a Docker container.

As of August 2015, the basic data entry, form generation and configuration logic is working and it is possible to create simple collections of data, supporting a limited range of data types including imported and linked images and audio files.  Missing core functionality intended for the initial release is generation of JSON-LD contexts for full linked data support.  Also intended for the initial release are usability improvements, notably in the area of simplifying the creation of some common data patterns (such as linked type, view and list definitions for new record types).

Note that all the active development takes place on the ["develop" branch](https://github.com/gklyne/annalist/tree/develop).  Tested versions are periodically merged to the default-visible 'master' branch.  In due course, I plan to follow a ["gitflow"-inspired](http://nvie.com/posts/a-successful-git-branching-model/) working style that uses the "master" branch for released, tested software.


Status
------

The [release notes](documents/release-notes/release-v0.1.md) give an summary of the current released state of the software.

Details of current feature development and status are available in the [TODO list](documents/TODO.md) and [GitHub issues](https://github.com/gklyne/annalist/issues).

Plans for future features and developments are sketched in the [Development roadmap](documents/roadmap.md).


Feedback
--------

Feedback can be provided via [annalist-discuss forum](https://groups.google.com/forum/#!forum/annalist-discuss) or [github issue tracker](https://github.com/gklyne/annalist/issues).


Development
-----------

Active development is taking place on the "develop" branch in GitHub - see [https://github.com/gklyne/annalist/tree/develop](https://github.com/gklyne/annalist/tree/develop)


Acknowledgements
----------------

Ideas motivating the creation of Annalist arose from discussions with past colleagues in the Zoology department at Oxford University, particularly Dr David Shotton who led the BioImage project, and Dr Helen White-Cooper who patiently explained her processes and data handling needs as a genomic researcher.

David Flanders, formerly of JISC and now at University of Melbourne, provided encouragement and support for the development of software tools to support academic activities, and in particular raising the profile of engineering and management skills needed to create effective software tools for academics.  A previous project, [Shuffl](https://code.google.com/p/shuffl/), conducted under a JISC Rapid Innovation program that he ran, provided many technical and management lessons that have contributed to the development of Annalist.

More recently, work in the European [Wf4Ever project](http://www.wf4ever-project.org), which explored the use of Research Objects to capture details of scientific method along with experimental data, raised many questions about the nature of tools needed to support publication of reproducible and re-usable research data.  The numerous discussions and experiments have informed many of the design ideas and choices that have gone in to Annalist.

----


