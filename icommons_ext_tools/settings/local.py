from .base import *
from logging.config import dictConfig

ALLOWED_HOSTS = ['*']

DEBUG = True

#  Dummy secret key value for testing and local usage
SECRET_KEY = "==$(1zr5hus_7r@)g4m^t@0qztiqeeeby5%r20q(sa2i^q@-0k"

INSTALLED_APPS += ('debug_toolbar', 'sslserver')

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

dictConfig(LOGGING)
