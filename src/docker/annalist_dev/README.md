# Building and publishing Docker images

This directory contains files to build a docker image running the development version of the Annalist software.  The software itself is loaded from the git 'develop' branch.  It is intended to be used mainly for testing the docker deployment structure and framework.

# Build instructions

NOTE: the commands below should be run with an installed copy of the annalist version to be containerized.  (The makefile uses `annlist-manager version` to retieve the current software version tag.)

The line:

    echo "2015-12-29T15:30"

in `Dockerfile` should be updated when the github repository `develop` branch is updated to force a new Docker image to be created with the latest copy of the Git repository content.

To build a local docker image, named `annalist_dev`, use the command:

    make all

To push a copy of the current image to DockerHub as `gklyne/annalist_dev` (which can take some time on a slow network connection), use:

    make push

# Some other useful Docker commands

Some of the following adapted from [http://jimhoskins.com/2013/07/27/remove-untagged-docker-images.html]()

Remove all images:

    docker rmi `docker images -aq`

Remove old "dangling" docker images:

    docker rmi $(docker images -f "dangling=true" -q)

Remove all containers:

   docker rm `docker ps -aq`

Remove all stopped containers:

    docker rm $(docker ps -a -q)

This should not remove any running containers, and it will tell you it can’t remove a running image.

Remove all untagged images:

    docker rm $(docker ps -a | grep -v 'annalist\|CONTAINER' | awk '{print $1}')

or

    docker rm $(docker ps -a |  awk '!/annalist|CONTAINER/ {print $1}')

