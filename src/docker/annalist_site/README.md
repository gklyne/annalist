# Building and publishing Docker images

This directory contains files to build a docker image to persist Annalist site data.

For more information about this pattern see:

* http://www.tech-d.net/2013/12/16/persistent-volumes-with-docker-container-as-volume-pattern/
* http://www.alexecollins.com/docker-persistence/

# Build instructions

To build a local docker image, named `annalist_site`, use the command:

    make all

To push a copy of the current image to DockerHub as `gklyne/annalist_site` (which can take some time on a slow network connection), use:

    make push

