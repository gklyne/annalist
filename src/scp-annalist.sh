#!/bin/bash

if [ "$1" == "" ]; then
     echo "Usage:"
     echo "  scp-annalist.sh file"
     echo "  scp-annalist.sh -r dir"
    exit
fi

scp -i ~/.ssh/id_rsa_openstack_gk $@ annalist@annalist.net:uploads

