export DJANGO_SETTINGS_MODULE=annalist_site.settings.personal_debug
python manage.py migrate
OAUTHLIB_INSECURE_TRANSPORT=1 python manage.py runserver 0.0.0.0:8000
unset DJANGO_SETTINGS_MODULE
