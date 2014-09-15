# Getting started with Annalist

A 6 minute demonstration screencast can be downloaded at [http://annalist.net](http://annalist.net)

# Install and initialize software

See [Installing and setting up Annalist](installing-annalist.md) for details.  What follows is just a very brief summary.

## Prerequisites

* A Unix-like operating system: Annalist has been tested with MacOS 10.9 and Linux 14.04.  Other versions should be usable.
* Python 2.7 (see [Python beginners guide / download](https://wiki.python.org/moin/BeginnersGuide/Download)).
* virtualenv (includes setuptools and pip; see [virtualenv introduction](http://virtualenv.readthedocs.org/en/latest/virtualenv.html)).

(The software can be run on Windows, but the procedure to get it running is somewhat more complicated, and is not yet fully tested or documented.)

## Installation

Download to a working directory from [http://annalist.net/software/Annalist-0.1.2.tar.gz]().

In working directory:

    virtualenv annenv
    . annenv/bin/activate
    pip install Annalist-0.1.2.tar.gz

## Check the software installation, and initialize site data

The following commands create an initialize an annalist site in the invoking user's home directory; i.e. `~/annalist_site`.  See [Installing and setting up Annalist](installing-annalist.md) for other options.

    annalist-manager runtests
    annalist-manager initialize
    annalist-manager createsitedata
    annalist-manager createadminuser

Enter a username, email address and password for the admin user as prompted.

## Start the server

    annalist-manager runserver


# Accessing and using annalist

See [Installing and setting up Annalist](installing-annalist.md) and [Guide to using Annalist](using-annalist.md) for details.  What follows is just a very brief summary to get started.

## Access annalist and create a collection

Browse to [http:/localhost:8000/](), log in using the admin account.

Fill in a collection name and short description in the boxes displayed, and click 'New'.

## Create, view and edit data

See the [demonstration screecast](http://annalist.net/media/annalist-demo-music-instrument-catalogue.mp4) for an introduction to using Annalist.

An Annalist _collection_ consists of entity _data records_, _types_, _lists_, _views_ and _fields_.  You can start to create data records using the defaults provided, and add fields to those records as needed.  Lusrt and view descriptions can be added to provide different ways to examine and update the data records.

See the [Guide to using Annalist](using-annalist.md) for details.

