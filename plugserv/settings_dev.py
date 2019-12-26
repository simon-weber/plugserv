from .settings import *  # noqa

SECRET_KEY = 'dev_secret_key'
DEBUG = True
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_BROWSER_XSS_FILTER = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
X_FRAME_OPTIONS = 'SAMEORIGIN'
USE_X_FORWARDED_HOST = False
SECURE_PROXY_SSL_HEADER = None

ALLOWED_HOSTS.append('*')

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'plugserv_db.sqlite3'),
    }
}

SEND_GA_EVENTS = False
EXAMPLE_SERVE_ID = os.environ.get('EXAMPLE_SERVE_ID', 'aa5bcf1d-27cd-48d7-897e-1e73ed9192b8')

# disable sentry
sentry_sdk.init(dsn='')  # noqa: F405

TLD_CACHE_PATH = os.path.join(BASE_DIR, 'tld.cache')
