# export DJANGO_SETTINGS_MODULE=annalist_site.settings.runtests
unset DJANGO_SETTINGS_MODULE
python manage.py test
