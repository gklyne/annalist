# Update test data in test/init directory

# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "rm -rf $BASEDIR/sampledata/testinit/annalist_site/c" 
rm -rf $BASEDIR/sampledata/testinit/annalist_site/c

echo "rm -rf $BASEDIR/sampledata/data/annalist_site/c" 
rm -rf $BASEDIR/sampledata/data/annalist_site/c

python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateTestSiteData

echo "cp -r $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/testinit/annalist_site/"
mkdir -p $BASEDIR/sampledata/testinit/annalist_site/
cp -r $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/testinit/annalist_site/
cp $BASEDIR/annalist/data/test/* $BASEDIR/sampledata/testinit/annalist_site/

# echo "cp $BASEDIR/sampledata/data/annalist_site/README.md $BASEDIR/sampledata/testinit/annalist_site/"
# cp $BASEDIR/sampledata/data/annalist_site/README.md $BASEDIR/sampledata/testinit/annalist_site/

# End.
