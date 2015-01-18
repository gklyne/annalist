FROM ubuntu

MAINTAINER Graham Klyne <gk-annalist@ninebynine.org>

RUN apt-get update -y  && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python-virtualenv && \
    apt-get install -y git

# RUN pip install annalist

# WORKDIR /annalist

RUN mkdir /github && \
    cd /github && \
    git clone https://github.com/gklyne/annalist.git

RUN cd /github/annalist/src && \
    git checkout develop && \
    python setup.py clean --all && \
    python setup.py build && \
    python setup.py install

VOLUME /annalist
ENV HOME /annalist

# ADD entrypoint.sh /entrypoint.sh

EXPOSE 8000

# CMD /entrypoint.sh


################################################################################

#!/bin/bash
#entrypoint.sh

# env var TERM is "dumb" for non-interactive docker, or "XTERM" for interactive

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




