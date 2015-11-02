# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# rm -rf $BASEDIR/sampledata/init/annalist_site/c
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateEmptySiteData
cp $BASEDIR/sampledata/data/annalist_site/_annalist_site/site_context.jsonld \
   $BASEDIR/sampledata/empty/annalist_site/_annalist_site/

# End.
