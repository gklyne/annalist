# Getting started with Annalist

A number of demonstration screencast videos, and accompanying scripts, can be found by browsing to the [demonstration/evaluation scripts](./demo-script.md) page.


# Quick deployment using Docker

## Prerequisites

* A Linux operating system with [Docker](https://www.docker.com) installed.

## Installation

To install and run Annalist in a docker container, use the following commands.

If Annalist docker containers have been used previously on the host system, the following commamnds ensure you have the latest images:

    docker pull gklyne/annalist_site
    docker pull gklyne/annalist

Then

    docker run --name=annalist_site --detach gklyne/annalist_site
    docker run --interactive --tty --rm \
        --publish=8000:8000 --volumes-from=annalist_site \
        gklyne/annalist bash

Then, in the presented shell environment:

    annalist-manager version

Check the version displayed: I've found docker sometimes caches older versions and fails up update to the latest available.  If necessary, use `docker rmi gklyne/annalist` to remove old images from the local cache.  If all is well, continue as follows:

    annalist-manager createsitedata
    annalist-manager initialize
    annalist-manager defaultadminuser  # Enter password when prompted
    annalist-manager runserver

Control-C shuts down the server, then `exit` or Control-D to shut down the Docker container.


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
    annalist-manager createsitedata
    annalist-manager initialize
    annalist-manager defaultadminuser

Enter and re-enter a password for the admin user when prompted.

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

See [Installing and setting up Annalist](installing-annalist.md) and [Guide to using Annalist](using-annalist.adoc) for details.  What follows is just a very brief summary to get started.

## Access annalist and create a collection

Browse to [http:/localhost:8000/](http:/localhost:8000/), log in using the admin account.

Fill in a collection name and short description in the boxes displayed, and click 'New'.

## Create, view and edit data

An Annalist _collection_ consists of entity _data records_, _types_, _lists_, _views_ and _fields_.  You can start to create data records using the defaults provided, and add fields to those records as needed.  Lusrt and view descriptions can be added to provide different ways to examine and update the data records.

See the [demonstration screecast](http://annalist.net/media/annalist-demo-music-instrument-catalogue.mp4) for an introduction to using Annalist.  The sequence of operations performed by demonstration is described in [documents/demo-script.md](demo-script.md).

See the [Guide to using Annalist](using-annalist.adoc) for details.

