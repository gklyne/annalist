# Update test data in test/init directory

# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SITEDIR="annalist_test"

echo "rm -rf $BASEDIR/sampledata/testinit/annalist_test/c" 
rm -rf $BASEDIR/sampledata/testinit/annalist_test/c

echo "rm -rf $BASEDIR/sampledata/data/annalist_test/c" 
rm -rf $BASEDIR/sampledata/data/annalist_test/c

python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateTestSiteData

echo "cp -r $BASEDIR/sampledata/data/annalist_test/c $BASEDIR/sampledata/testinit/annalist_test/"
mkdir -p $BASEDIR/sampledata/testinit/annalist_test/
cp -r $BASEDIR/sampledata/data/annalist_test/c $BASEDIR/sampledata/testinit/annalist_test/
cp $BASEDIR/annalist/data/test/* $BASEDIR/sampledata/testinit/annalist_test/

# echo "cp $BASEDIR/sampledata/data/annalist_test/README.md $BASEDIR/sampledata/testinit/annalist_test/"
# cp $BASEDIR/sampledata/data/annalist_test/README.md $BASEDIR/sampledata/testinit/annalist_test/

# End.
