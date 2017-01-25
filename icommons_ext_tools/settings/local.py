from .base import *
from logging.config import dictConfig

ALLOWED_HOSTS = ['*']

DEBUG = True

SECRET_KEY = "==$(1zr5hus_7r@)g4m^t@0qztiqeeeby5%r20q(sa2i^q@-0k"

# To allow local development server to load static files with DEBUG=False, run:
#   manage.py runserver --insecure
# Note: this should never be done for anything but protected local development purposes.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

CANVAS_EMAIL_NOTIFICATION['course_migration_success_subject'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['course_migration_failure_subject'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['support_email_subject_on_failure'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['support_email_address'] = 'tltqaemails@g.harvard.edu'

# need to override the NLS_DATE_FORMAT that is set by oraclepool

INSTALLED_APPS += ('debug_toolbar', 'sslserver')

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)

# Log to console instead of a file when running locally
LOGGING['handlers']['default'] = {
    'level': logging.DEBUG,
    'class': 'logging.StreamHandler',
    'formatter': 'simple',
}

dictConfig(LOGGING)
