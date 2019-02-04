# Run development server for FAST project data
# This can serve as an example for running Annalist with alternative site data.
export DJANGO_SETTINGS_MODULE=annalist_site.settings.fast_project
python manage.py migrate
OAUTHLIB_INSECURE_TRANSPORT=1 python manage.py rundevserver 0.0.0.0:8000
unset DJANGO_SETTINGS_MODULE
