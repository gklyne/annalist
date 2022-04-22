# Automated steps for preparing new Annalist release

pip uninstall -y annalist
# python setup.py clean --all
git clean -fX
pip install .
# python setup.py build
# python setup.py install
annalist-manager runtest
annalist-manager updatesite
annalist-manager initialize

annalist-manager installcoll RDF_schema_defs --force
annalist-manager installcoll Annalist_schema --force
annalist-manager migratecoll RDF_schema_defs
less "$HOME/annalist_site/annalist.log"
annalist-manager migratecoll Annalist_schema
less "$HOME/annalist_site/annalist.log"

