# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -rf $BASEDIR/sampledata/init/annalist_site/c
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateEmptySiteData
# Temporary - later, use personal and/or shared site
cp -rv $BASEDIR/sampledata/init/annalist_site/ $BASEDIR/devel/
# cp -rv $BASEDIR/sampledata/data/annalist_site/c $BASEDIR/sampledata/init/annalist_site/

# End.
