#!/usr/bin/env bash

echo "Copying: ../documents/pages  ->  annalist@annalist.net:uploads"
scp -i ~/.ssh/id_rsa_openstack_gk \
    -r ../documents/pages annalist@annalist.net:uploads

echo "Copying ../documents/tutorial  ->  annalist@annalist.net:uploads/documents"
scp -i ~/.ssh/id_rsa_openstack_gk \
    -r ../documents/tutorial annalist@annalist.net:uploads/documents

