from .base import *

# To allow local development server to load static files with DEBUG=False, run:
#   manage.py runserver --insecure
# Note: this should never be done for anything but protected local development purposes.
DEBUG = True
TEMPLATE_DEBUG = DEBUG
CRISPY_FAIL_SILENTLY = not DEBUG

# LOG_ROOT used for log file storage; EMAIL_FILE_PATH used for
# email output if EMAIL_BACKEND is filebased.EmailBackend

ISITES_LMS_URL = 'http://isites.harvard.edu/'


CANVAS_EMAIL_NOTIFICATION['course_migration_success_subject'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['course_migration_failure_subject'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['support_email_subject_on_failure'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['environment'] = 'Local'
CANVAS_EMAIL_NOTIFICATION['support_email_address'] = 'tltqaemails@g.harvard.edu'

COURSE_WIZARD['TERM_TOOL_BASE_URL'] = 'https://localhost:8000'

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.oracle',

        'NAME': 'isiteqa',
        'USER': SECURE_SETTINGS['django_db_user'],
        'PASSWORD': SECURE_SETTINGS['django_db_pass'],
        'HOST': 'icd3.isites.harvard.edu',

        'PORT': '8003',
        'OPTIONS': {
            'threaded': True,
        },

        'CONN_MAX_AGE': 0,
    }
}

DATABASE_ROUTERS = ['icommons_common.routers.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    'canvas_course_site_wizard': 'default',
}
DATABASE_MIGRATION_WHITELIST = ['default']

# need to override the NLS_DATE_FORMAT that is set by oraclepool
'''
DATABASE_EXTRAS = {
    'session': ["ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'", ],
    'threaded': True,
}
'''

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

'''
The dictionary below contains group id's and school names.
These are the groups that are allowed to edit term informtion.
The school must be the same as the school_id in the school model.
'''
