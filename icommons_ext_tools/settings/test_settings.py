from .base import *

# NOTE: during tests email is saved in django.core.mail.outbox and no real email is sent

DATABASE_ROUTERS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'icommons_ext_tools.db.sqlite3',
    },
}

ISITES_LMS_URL = ''
