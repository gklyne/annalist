# Building and publishing Docker images

This directory contains files to build a docker image running the development version of the Annalist software.  The software itself is loaded from the git 'develop' branch.  It is intended to be used mainly for testing the docker deployment structure and framework.

# Build instructions

The line:

    echo "2015-12-29T15:30"

in `Dockerfile` should be updated when the github repository `develop` branch is updated to force a new Docker image to be created with the latest copy of the Git repository content.

To build a local docker image, named `annalist_dev`, use the command:

    make all

To push a copy of the current image to DockerHub as `gklyne/annalist_dev` (which can take some time on a slow network connection), use:

    make push

# Some other useful Docker commands

Remove old "dangling" docker images:

    docker rmi $(docker images -f "dangling=true" -q)

Remove all containers:

   docker rm `docker ps -aq`

Remove all images:

    docker rmi `docker images -aq`


