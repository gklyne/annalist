#!/usr/bin/env bash

echo "Install supplied collection data in an annalist site."
echo "(Assumes Python virtualenv is activated with Annalist installed.)"
echo ""

rm -rf $(annalist-manager sitedirectory --personal)/c/Resource_defs
annalist-manager installcoll Resource_defs

rm -rf $(annalist-manager sitedirectory --personal)/c/Concept_defs
annalist-manager installcoll Concept_defs

rm -rf $(annalist-manager sitedirectory --personal)/c/Journal_defs
annalist-manager installcoll Journal_defs

rm -rf $(annalist-manager sitedirectory --personal)/c/RDF_schema_defs
annalist-manager installcoll RDF_schema_defs

rm -rf $(annalist-manager sitedirectory --personal)/c/Annalist_schema
annalist-manager installcoll Annalist_schema

echo "To run Annalist:"
echo "    annalist-manager runserver"
echo "or:"
echo "    nohup annalist-manager runserver >annalist.out &"

# End.
