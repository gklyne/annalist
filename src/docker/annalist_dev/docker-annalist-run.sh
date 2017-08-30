#!/bin/bash

HOSTPORT=8000
GUESTPORT=8000
DATA_CONTAINER=annalist_site
IMAGE=annalist_dev
RELEASE=0.5.4
docker run -it -p ${HOSTPORT}:${GUESTPORT} --volumes-from=${DATA_CONTAINER} ${IMAGE}:${RELEASE}

