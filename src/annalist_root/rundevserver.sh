# Run development server
# See also: gunicorn_server
export DJANGO_SETTINGS_MODULE=annalist_site.settings.personal
python manage.py migrate
OAUTHLIB_INSECURE_TRANSPORT=1 python manage.py rundevserver 0.0.0.0:8000
unset DJANGO_SETTINGS_MODULE
