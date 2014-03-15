# update test data in test/inkit and devel directories
BASEDIR=/Users/graham/workspace/github/gklyne/annalist/src/annalist_site

rm -rf $BASEDIR/test/init/annalist_site/c
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateDevelSiteData
cp -rv $BASEDIR/test/data/annalist_site $BASEDIR/devel/

rm -rf $BASEDIR/test/init/annalist_site/c
mv $BASEDIR/devel/annalist_site $BASEDIR/devel/annalist_site_old
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateTestSiteData
cp -rv $BASEDIR/test/data/annalist_site/c $BASEDIR/test/init/annalist_site/

# End.