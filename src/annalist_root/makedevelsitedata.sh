# update test data in devel directory.  Data in sampledata/init is removed and regenerated
# 
# BASEDIR=/Users/graham/workspace/github/gklyne/annalist/src/annalist_root

# See: http://stackoverflow.com/questions/59895/
BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

rm -rf $BASEDIR/sampledata/init/annalist_site/c
python manage.py test annalist.tests.test_createsitedata.CreateSiteData.test_CreateDevelSiteData
rm -rf $BASEDIR/devel/annalist_site_backup
mv $BASEDIR/devel/annalist_site $BASEDIR/devel/annalist_site_backup
cp -rv $BASEDIR/sampledata/data/annalist_site $BASEDIR/devel/

source makeinitsitedata.sh

# End.
