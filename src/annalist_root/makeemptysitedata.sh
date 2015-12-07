# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "rm -rf $BASEDIR/sampledata/empty/annalist_site/c" 
rm -rf $BASEDIR/sampledata/empty/annalist_site/c

echo "rm -rf $BASEDIR/sampledata/data/annalist_site/c" 
rm -rf $BASEDIR/sampledata/data/annalist_site/c

python manage.py test \
    annalist.tests.test_createsitedata.CreateSiteData.test_CreateEmptySiteData

echo "cp -r $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/empty/annalist_site/"
mkdir -p $BASEDIR/sampledata/empty/annalist_site/
cp -r $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/empty/annalist_site/

echo "cp $BASEDIR/sampledata/data/annalist_site/README.md $BASEDIR/sampledata/empty/annalist_site/"
cp $BASEDIR/sampledata/data/annalist_site/README.md $BASEDIR/sampledata/empty/annalist_site/

# End.
