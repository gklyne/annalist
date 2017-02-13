# Building and publishing Docker images

This directory contains files to build a docker image running the released version of the Annalist software.  The software itself is loaded from thge Python Package Index (PyPI) using `pip`.

# Build instructions

NOTE: the commands below should be run with an installed copy of the annalist version to be containerized.  (The makefile uses `annlist-manager version` to retieve the current software version tag.)

@@TODO: check this

The line:

    RUN pip install annalist=0.1.36

in `Dockerfile` should be updated a new release of Annalist is created, to ensure a new Docker image is created as needed.

To build a local docker image, named `annalist`, use the command:

    make all

To push a copy of the current image to DockerHub as `gklyne/annalist` (which can take some time on a slow network connection), use:

    make push

