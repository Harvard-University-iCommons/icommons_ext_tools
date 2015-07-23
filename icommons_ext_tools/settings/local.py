from .base import *

# To allow local development server to load static files with DEBUG=False, run:
#   manage.py runserver --insecure
# Note: this should never be done for anything but protected local development purposes.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


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

# need to override the NLS_DATE_FORMAT that is set by oraclepool

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

'''
The dictionary below contains group id's and school names.
These are the groups that are allowed to edit term informtion.
The school must be the same as the school_id in the school model.
'''
