# update test data in test/init directory

# BASEDIR=/Users/graham/workspace/github/gklyne/annalist/src/annalist_root

# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -rf $BASEDIR/sampledata/init/annalist_site/c
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateTestSiteData
cp -rv $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/init/annalist_site/

# End.
