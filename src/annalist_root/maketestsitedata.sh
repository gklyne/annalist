# Update test data in test/init directory

# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "rm -rf $BASEDIR/sampledata/init/annalist_site/c" 
rm -rf $BASEDIR/sampledata/init/annalist_site/c

echo "rm -rf $BASEDIR/sampledata/data/annalist_site/c" 
rm -rf $BASEDIR/sampledata/data/annalist_site/c

python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateTestSiteData

echo "cp -r $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/init/annalist_site/"
cp -r $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/init/annalist_site/

# End.
