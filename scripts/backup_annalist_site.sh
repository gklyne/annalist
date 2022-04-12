#!/usr/bin/env bash

mkdir ~/annalist_site_backup/
SRC=$(annalist-manager sitedirectory)
DST=~/annalist_site_backup/annalist_site-$(date "+%Y-%m-%d")
echo Backing up annalist site at $SRC
cp -rv $SRC $DST
echo Copied files from $SRC to $DST
