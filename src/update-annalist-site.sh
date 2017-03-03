#!/usr/bin/env bash

echo "Update Annalist site data for installed software"
echo ""

killall python
annalist-manager initialize --personal
annalist-manager updatesite --personal

# Update all installable collections

rm -rf $(annalist-manager sitedirectory --personal)/c/Bibliography_defs
annalist-manager installcoll Bibliography_defs

rm -rf $(annalist-manager sitedirectory --personal)/c/Journal_defs
annalist-manager installcoll Journal_defs

rm -rf $(annalist-manager sitedirectory --personal)/c/RDF_schema_defs
annalist-manager installcoll RDF_schema_defs

rm -rf $(annalist-manager sitedirectory --personal)/c/Annalist_schema
annalist-manager installcoll Annalist_schema

echo "To run Annalist: 'annalist-manager runserver'"

# End.
