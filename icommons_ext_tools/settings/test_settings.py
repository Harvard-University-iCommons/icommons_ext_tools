from .base import *

# NOTE: during tests email is saved in django.core.mail.outbox and no real email is sent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'icommons_ext_tools.db.sqlite3',
    },
}

DATABASE_ROUTERS = ['icommons_common.routers.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {
    'canvas_course_site_wizard': 'default',
    'auth': 'default',
    'contenttypes': 'default',
    'sessions': 'default',
}
DATABASE_MIGRATION_WHITELIST = ['default']

ISITES_LMS_URL = ''
