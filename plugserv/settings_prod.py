from .settings import *  # noqa

# These are overridden or ignored in settings_dev,
# but putting them outside the import path avoids dummy secrets in dev
# (and enforces their presence in prod).

ALLOWED_HOSTS = [os.environ['SITE']]

SECRET_KEY = os.environ['SECRET_KEY']
AWS_ACCESS_KEY_ID = os.environ['SES_ID']
AWS_SECRET_ACCESS_KEY = os.environ['SES_KEY']

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.WARNING,
)
sentry_sdk.init(
    dsn=os.environ['SENTRY_DSN'],
    integrations=[
        DjangoIntegration(),
        sentry_logging,
    ],
)
