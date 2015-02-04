from .base import *

# NOTE: during tests email is saved in django.core.mail.outbox and no real email is sent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'icommons_ext_tools.db.sqlite3',
    },
}

ISITES_LMS_URL = ''

# NOTE: once the canvas_course_wizard application is removed we can eliminate it's
# inclusion below.  Only reason to include it here is to allow for unit tests to work.
INSTALLED_APPS += (
    'canvas_course_wizard',
)
