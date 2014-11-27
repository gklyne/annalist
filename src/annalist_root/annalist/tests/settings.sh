# Create environment variables to run test module in isolation
#
# Execute with:
#
#   . settings.sh
#
export PYTHONPATH=../..:../templates
export DJANGO_SETTINGS_MODULE=annalist_site.settings.runtests
