# Update development site data from source directories
#
# NOTE: do not delete _annalist_site/site_meta.jsonld from the target site 
# when updating site data:  that file is site-specific.

cp -rv annalist/sitedata/* devel/annalist_site/_annalist_site/

# End.
