#!/usr/bin/env bash

if [ "$1" == "" ]; then
     echo "Usage:"
     echo "  ssh-annalist.sh"
    exit
fi

ssh -i ~/.ssh/id_rsa_openstack_gk annalist@annalist.net
