# Test script for running Annalisrt using a gunicorn HTTP server rather than
# the Django development server via via manage.py.  
# The development server is not recommended for production use.

# Note: limit to 1 worker process because of data caching and cache invalidation.
# @@TODO: figure out how to make caches work properly with multiple workers.

gunicorn --workers=1 \
    --bind=0.0.0.0:8000 \
    --env DJANGO_SETTINGS_MODULE=annalist_site.settings.personal \
    --env OAUTHLIB_INSECURE_TRANSPORT=1 \
    --access-logfile annalist-access.log \
    --error-logfile  annalist-error.log \
    annalist_site.wsgi:application

# End
