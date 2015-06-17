from .base import *

DEBUG = False

ALLOWED_HOSTS = ['*']

# Update qualtrics term urls in prod
QUALTRICS_LINK['USER_DECLINED_TERMS_URL'] = 'http://surveytools.harvard.edu'
QUALTRICS_LINK['USER_ACCEPTED_TERMS_URL'] = 'ql:launch'

ISITES_LMS_URL = 'http://isites.harvard.edu/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'isitedgd',
        'USER': SECURE_SETTINGS.get('django_db_user'),
        'PASSWORD': SECURE_SETTINGS.get('django_db_pass'),
        'HOST': 'dbnode3.isites.harvard.edu',
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
