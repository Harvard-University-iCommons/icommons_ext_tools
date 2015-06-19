# test.py
from .base import *
DEBUG = True

ALLOWED_HOSTS = ['*']

ISITES_LMS_URL = 'http://qa.isites.harvard.edu/'

CANVAS_EMAIL_NOTIFICATION['course_migration_success_subject'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['course_migration_failure_subject'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['support_email_subject_on_failure'] += ' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['environment'] = 'Test'
CANVAS_EMAIL_NOTIFICATION['support_email_address'] = 'tltqaemails@g.harvard.edu'

COURSE_WIZARD['TERM_TOOL_BASE_URL'] = 'https://test.tlt.harvard.edu'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'isiteqa',
        'USER': SECURE_SETTINGS.get('django_db_user', None),
        'PASSWORD': SECURE_SETTINGS.get('django_db_pass', None),
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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
