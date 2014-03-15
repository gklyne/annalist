# update test data in devel directory.  Data in test/init is remioved and regenerated
BASEDIR=/Users/graham/workspace/github/gklyne/annalist/src/annalist_site

rm -rf $BASEDIR/test/init/annalist_site/c
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateDevelSiteData
mv $BASEDIR/devel/annalist_site $BASEDIR/devel/annalist_site_old
cp -rv $BASEDIR/test/data/annalist_site $BASEDIR/devel/

source makeinitsitedata.sh

# End.
