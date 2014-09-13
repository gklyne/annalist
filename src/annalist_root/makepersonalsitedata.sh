# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -rf $BASEDIR/sampledata/init/annalist_site/c
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateEmptySiteData
cp -rv $BASEDIR/sampledata/data/annalist_site/c ~/annalist_site/

# End.
