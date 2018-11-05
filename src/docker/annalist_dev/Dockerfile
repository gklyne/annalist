FROM ubuntu:18.04

MAINTAINER Graham Klyne <gk-annalist@ninebynine.org>

RUN apt-get update -y  && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python-virtualenv && \
    apt-get install -y git

RUN mkdir /github && \
    cd /github && \
    git clone https://github.com/gklyne/annalist.git && \
    cd /github/annalist/src && \
    git checkout develop && \
    git pull && \
    python setup.py clean --all && \
    python setup.py build && \
    python setup.py install && \
    echo "2018-10-26" # (see https://github.com/docker/docker/issues/1326#issuecomment-52304721)

VOLUME /annalist_site
ENV HOME=/annalist_site \
    OAUTHLIB_INSECURE_TRANSPORT=1

EXPOSE 8000

CMD annalist-manager runserver

# ADD entrypoint.sh /entrypoint.sh

# CMD /entrypoint.sh

################################################################################

#!/bin/bash
#entrypoint.sh
#
# env var TERM is "dumb" for non-interactive docker, or "XTERM" for interactive
#
# if ! [[ -r /flag_annalist_installed ]]; then
# 
#     annalist-manager createsitedata
#     annalist-manager initialize
#     annalist-manager defaultadmin
# 
#     touch /flag_annalist_installed
# 
# fi

# annalist-manager runserver

