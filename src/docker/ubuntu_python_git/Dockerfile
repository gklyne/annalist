# Build a base Ubuntu kit for installing Annalist:
# Includes base system updates, Python and git

FROM ubuntu

MAINTAINER Graham Klyne <gk-annalist@ninebynine.org>

RUN apt-get update -y  && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python-virtualenv && \
    apt-get install -y git

RUN mkdir /github && \
    cd /github && \
    git clone https://github.com/gklyne/annalist.git

