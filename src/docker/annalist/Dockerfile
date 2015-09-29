FROM ubuntu

MAINTAINER Graham Klyne <gk-annalist@ninebynine.org>

RUN apt-get update -y  && \
    apt-get upgrade -y && \
    apt-get install -y python python-pip python-virtualenv && \
    apt-get install -y git

RUN pip install annalist==0.1.20

VOLUME /annalist_site
ENV HOME /annalist_site

EXPOSE 8000

CMD annalist-manager runserver

