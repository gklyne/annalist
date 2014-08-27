# Remove environment variables used to run test module in isolation
# (cf. annalist/tests/settings.sh)
#
# Execute with:
#   . settings.sh
#
unset PYTHONPATH
unset DJANGO_SETTINGS_MODULE
# export DJANGO_SETTINGS_MODULE=annalist_site.settings.devel
