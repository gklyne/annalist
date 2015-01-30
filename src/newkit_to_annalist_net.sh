python setup.py build sdist
scp -i ~/.ssh/id_rsa_openstack_gk \
    dist/Annalist-0.1.10.tar.gz annalist@annalist.net:/var/www/software

scp -i ~/.ssh/id_rsa_openstack_gk \
    -r ../documents/pages annalist@annalist.net:uploads
