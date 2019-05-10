FROM ubuntu:18.04

MAINTAINER Graham Klyne <gk-annalist@ninebynine.org>

RUN apt-get update -y  && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python-virtualenv && \
    apt-get install -y git

RUN pip install annalist==0.5.16

VOLUME /annalist_site
ENV HOME=/annalist_site \
    OAUTHLIB_INSECURE_TRANSPORT=1

EXPOSE 8000

CMD annalist-manager runserver

