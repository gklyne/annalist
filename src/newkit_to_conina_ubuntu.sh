python setup.py build sdist
scp -i ~/.ssh/id_rsa_openstack_gk \
    dist/Annalist-0.1.28.tar.gz  annalist@conina-ubuntu:

