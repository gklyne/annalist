FROM ubuntu

MAINTAINER Graham Klyne <gk-annalist@ninebynine.org>

RUN apt-get update -y  && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python-virtualenv && \
    apt-get install -y git

RUN pip install django==1.7 wsgiref==0.1.2 oauth2client==1.2 httplib2==0.9

RUN mkdir /github && \
    cd /github && \
    git clone https://github.com/gklyne/annalist.git

RUN cd /github/annalist/src && \
    git checkout develop && \
    git pull && \
    python setup.py clean --all && \
    python setup.py build && \
    python setup.py install && \
    echo "2015-12-29T15:30" # (see https://github.com/docker/docker/issues/1326#issuecomment-52304721)

VOLUME /annalist_site
ENV HOME /annalist_site

EXPOSE 8000

CMD annalist-manager runserver

# ADD entrypoint.sh /entrypoint.sh

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

