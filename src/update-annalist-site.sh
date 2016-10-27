echo "Update Annalist site data for installed software"
echo ""

killall python
annalist-manager initialize --personal
annalist-manager updatesite --personal

rm -rf $(annalist-manager sitedirectory --personal)/c/Bibliography_defs
annalist-manager installcoll Bibliography_defs

echo "To run Annalist: 'annalist-manager runserver'"

# End.
