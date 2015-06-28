echo "Assumes annalist environment has been activated, and latest software installed"
echo "e.g."
echo "    source anenv/bin/activate"
echo "    pip install /var/www/software/Annalist-0.1.xx.tar.gz --upgrade"
echo "    annalist-manager runtests"
echo ""

killall python
annalist-manager initialize --personal
annalist-manager updatesite --personal
nohup annalist-manager runserver --personal >annalist.out &

# End.
