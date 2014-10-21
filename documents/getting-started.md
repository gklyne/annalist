# Getting started with Annalist

A 6 minute demonstration screencast can be downloaded at [http://annalist.net](http://annalist.net)


# Install and initialize software

See [Installing and setting up Annalist](installing-annalist.md) for details.  What follows is just a very brief summary.

## Prerequisites

* A Unix-like operating system.
* Python 2.7.
* virtualenv.

(The software can be run on Windows, but the procedure to get it running is somewhat more complicated, and is not yet fully tested or documented.)

## Installation

In a working directory, and with Internet connection:

    virtualenv annenv
    source annenv/bin/activate
    pip install annalist

## Check the software installation, and initialize site data

The following commands create an initialize an annalist site in the invoking user's home directory; i.e. `~/annalist_site`.  See [Installing and setting up Annalist](installing-annalist.md) for other options.

    annalist-manager runtests
    annalist-manager initialize
    annalist-manager createsitedata
    annalist-manager createadminuser

Enter a username, email address and password for the admin user as prompted.

## Start the server

    annalist-manager runserver


# Update an existing installation

> @@TODO: test this

Backup the current installation and site data, just in case.

NOTE that reinstalling the software currently wipes any locally defined user credentials:  locally defined users must be re-created using the `annalist-manager createadminuser` command and/or through the werbsite `admin` link.

## Upgrade software and test

Install updated software into existing Python virtual environment:

    source annenv/bin/activate
    pip install annalist --upgrade
    annalist-manager runtests

## Update site data

    annalist-manager initialize
    annalist-manager updatesitedata

Locally defined admin user credential should be re-created:

    annalist-manager createadminuser

Existing user permissions are carried over from the previous installation.

## Start the server

    annalist-manager runserver


# Accessing and using annalist

See [Installing and setting up Annalist](installing-annalist.md) and [Guide to using Annalist](using-annalist.md) for details.  What follows is just a very brief summary to get started.

## Access annalist and create a collection

Browse to [http:/localhost:8000/](http:/localhost:8000/), log in using the admin account.

Fill in a collection name and short description in the boxes displayed, and click 'New'.

## Create, view and edit data

An Annalist _collection_ consists of entity _data records_, _types_, _lists_, _views_ and _fields_.  You can start to create data records using the defaults provided, and add fields to those records as needed.  Lusrt and view descriptions can be added to provide different ways to examine and update the data records.

See the [demonstration screecast](http://annalist.net/media/annalist-demo-music-instrument-catalogue.mp4) for an introduction to using Annalist.  The sequence of operations performed by demonstration is described in [documents/demo-script.md](demo-script.md).

See the [Guide to using Annalist](using-annalist.md) for details.

