# Run Annalist under gunicorn server in personal configuration without HTTPS front-end
# See also: gunicorn_server
export DJANGO_SETTINGS_MODULE=annalist_site.settings.personal
python manage.py migrate
OAUTHLIB_INSECURE_TRANSPORT=1 annalist-manager runserver $1
unset DJANGO_SETTINGS_MODULE

