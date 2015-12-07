python setup.py clean --all
python setup.py build sdist

echo "Copying: dist/Annalist-0.1.24.tar.gz  ->  annalist@annalist.net:/var/www/software"
scp -i ~/.ssh/id_rsa_openstack_gk \
    dist/Annalist-0.1.24.tar.gz annalist@annalist.net:/var/www/software

echo "Copying: ../documents/pages  ->  annalist@annalist.net:uploads"
scp -i ~/.ssh/id_rsa_openstack_gk \
    -r ../documents/pages annalist@annalist.net:uploads

echo "Copying ../documents/tutorial  ->  annalist@annalist.net:uploads/documents"
scp -i ~/.ssh/id_rsa_openstack_gk \
    -r ../documents/tutorial annalist@annalist.net:uploads/documents

