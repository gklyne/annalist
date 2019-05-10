# Test script for running Annalist using a gunicorn HTTP server rather than
# the Django development server via via manage.py.
# This script is ***not*** for production use.

# Note: needs at least 2 threads to prevent deadlock when retrieving Turtle, 
# which uses internal HTTP request to access context to parse JSON-LD
# (This is the RDF library parser, so I can't easily intercept this)

gunicorn --workers=1 --threads=2 \
    --bind=0.0.0.0:8000 \
    --env DJANGO_SETTINGS_MODULE=annalist_site.settings.personal \
    --env ANNALIST_KEY=local_testing_key \
    --env OAUTHLIB_INSECURE_TRANSPORT=1 \
    --access-logfile annalist-access.log \
    --error-logfile  annalist-error.log \
    annalist_site.wsgi:application

# End
