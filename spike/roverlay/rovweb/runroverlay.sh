#! /bin/bash
echo "Sending service output to rovweb.log"

nohup python manage.py runserver 0.0.0.0:8000 >rovweb.log &

# End.
