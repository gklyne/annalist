#!/bin/bash
# docker run -it -p 8000:8000 --rm --volumes-from=annalist_site  annalist:0.1.9 bash

HOSTPORT=8000
GUESTPORT=8000
DATA_CONTAINER=annalist_site
IMAGE=annalist_dev
RELEASE=0.1.9
docker run -it -p ${HOSTPORT}:${GUESTPORT} --volumes-from=${DATA_CONTAINER} ${IMAGE}:${RELEASE}

