# plugserv
Shamelessly plug your projects across your own sites.

Sign up at https://www.plugserv.com to use it.

## development

The project layout is:
* ansible: deployments
* nix: infra/config management
* plugserv: django app
* secrets: prod secrets (managed with transcypt)

To run it (from inside a Python 3 virtualenv):
* `pip install -r dev-requirements.txt`
* `export DJANGO_SETTINGS_MODULE=plugserv.settings_dev`
* `python manage.py migrate`
* `python manage.py runserver`
* sign up, create a plug, `export EXAMPLE_SERVE_ID=<serve id for that user>`
