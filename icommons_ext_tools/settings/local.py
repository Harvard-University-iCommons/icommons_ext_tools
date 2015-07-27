from .base import *

# To allow local development server to load static files with DEBUG=False, run:
#   manage.py runserver --insecure
# Note: this should never be done for anything but protected local development purposes.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# need to override the NLS_DATE_FORMAT that is set by oraclepool

INSTALLED_APPS += ('debug_toolbar',)

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
