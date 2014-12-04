from .base import *
from .secure import SECURE_SETTINGS

# To allow local development server to load static files with DEBUG=False, run:
#   manage.py runserver --insecure
# Note: this should never be done for anything but protected local development purposes.
DEBUG = True
TEMPLATE_DEBUG = DEBUG
CRISPY_FAIL_SILENTLY = not DEBUG

# LOG_ROOT used for log file storage; EMAIL_FILE_PATH used for
# email output if EMAIL_BACKEND is filebased.EmailBackend
LOG_ROOT = join(SITE_ROOT, 'logs/')
EMAIL_FILE_PATH = LOG_ROOT

# sets 'from' email to show project and settings file name when sending emails to ADMINS
SERVER_EMAIL_DISPLAY_NAME = '%s - %s' % (PROJECT_NAME, get_settings_file_name(__file__))
SERVER_EMAIL = '%s <%s>' % (SERVER_EMAIL_DISPLAY_NAME, SERVER_EMAIL_EMAIL_ADDR)

ICOMMONS_COMMON = {

    'ICOMMONS_API_HOST': 'https://qa.isites.harvard.edu/services/',
    'ICOMMONS_API_USER': SECURE_SETTINGS['icommons_api_user'],
    'ICOMMONS_API_PASS': SECURE_SETTINGS['icommons_api_pass'],
}

ISITES_LMS_URL = 'http://isites.harvard.edu/'

CANVAS_WIZARD = {
    'TOKEN' : SECURE_SETTINGS['TOKEN'],
}

COURSE_WIZARD = {
    'OLD_LMS_URL' : SECURE_SETTINGS['OLD_LMS_URL'],
}

QUALTRICS_LINK = {

    'AGREEMENT_ID' : SECURE_SETTINGS['qualtrics_agreement_id'],
    'QUALTRICS_APP_KEY' : SECURE_SETTINGS['qualtrics_app_key'],
    'QUALTRICS_API_URL' : SECURE_SETTINGS['qualtrics_api_url'],
    'QUALTRICS_API_USER' : SECURE_SETTINGS['qualtrics_api_user'],
    'QUALTRICS_API_TOKEN' : SECURE_SETTINGS['qualtrics_api_token'],
    'QUALTRICS_AUTH_GROUP' : SECURE_SETTINGS['qualtrics_auth_group'],
    #'USER_DECLINED_TERMS_URL' : 'http://surveytools.harvard.edu',
    'USER_DECLINED_TERMS_URL' : 'ql:internal', # only in QA
    'USER_ACCEPTED_TERMS_URL' : 'ql:internal', # only in QA
}

CANVAS_SITE_SETTINGS = {
    'base_url': 'https://canvas.icommons.harvard.edu/',

}

CANVAS_EMAIL_NOTIFICATION['course_migration_success_subject'] = CANVAS_EMAIL_NOTIFICATION['course_migration_success_subject']+' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['course_migration_failure_subject'] = CANVAS_EMAIL_NOTIFICATION['course_migration_failure_subject']+' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['support_email_subject_on_failure'] = CANVAS_EMAIL_NOTIFICATION['support_email_subject_on_failure']+' (TEST, PLEASE IGNORE)'
CANVAS_EMAIL_NOTIFICATION['environment'] = 'Local'


CANVAS_SDK_SETTINGS = {
    'auth_token': SECURE_SETTINGS.get('canvas_token', None),
    'base_api_url': CANVAS_SITE_SETTINGS['base_url'] + 'api',
    'max_retries': 3,
    'per_page': 40,
}

DATABASES = {

    'default': {
        'ENGINE': 'django.db.backends.oracle',

       # DEV
       # 'NAME': 'isitedev',
       # 'USER': SECURE_SETTINGS['django_db_user'],
       # 'PASSWORD': SECURE_SETTINGS['django_db_pass'],
       # 'HOST': 'icd3.isites.harvard.edu',
       # 'PORT': '8103',
        'NAME': 'isiteqa',
        'USER': SECURE_SETTINGS['django_db_user'],
        'PASSWORD': SECURE_SETTINGS['django_db_pass_qa'],
        'HOST': 'icd3.isites.harvard.edu',

        'PORT': '8003',
         'OPTIONS': {
             'threaded': True,
         },

         'CONN_MAX_AGE': 0,

        # QA
        # 'default': {
        #     'ENGINE': 'django.db.backends.oracle',
        #     'NAME': 'isiteqa',
        #     'USER': SECURE_SETTINGS['django_db_user'],
        #     'PASSWORD': SECURE_SETTINGS['django_db_pass'],
        #     'HOST': 'icd3.isites.harvard.edu',
        #     'PORT': '8003',
        #     'OPTIONS': {
        #         'threaded': True,
        #     },
        #     'CONN_MAX_AGE': 0,
        # }

     }
 }


# need to override the NLS_DATE_FORMAT that is set by oraclepool
'''
DATABASE_EXTRAS = {
    'session': ["ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'", ],
    'threaded': True,
}
'''

STATIC_ROOT = normpath(join(SITE_ROOT, 'http_static'))

INSTALLED_APPS += (
    'debug_toolbar',
    'rest_framework.authtoken',
)

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

# For Django Debug Toolbar:
INTERNAL_IPS = ('127.0.0.1', '10.0.2.2',)
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(message)s'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        # Log to a text file that can be rotated by logrotate
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': join(LOG_ROOT, 'icommons_ext_tools.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'canvas_wizard': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'qualtrics_link': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'canvas_course_site_wizard': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'icommons_common': {
            'handlers': ['mail_admins', 'console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'icommons_ui': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        # Apps can log to tech_mail to selectively send ERROR emails to ADMINS
        'tech_mail': {
            'handlers': ['mail_admins', 'console', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'oraclepool': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'huey.consumer': {
            'handlers': ['logfile'],
            'level': 'INFO',
            'propagate': True,
        },
        'rest_framework': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends.oracle': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'canvas_shopping': {
            'handlers': ['mail_admins', 'console', 'logfile', ],
            'level': 'DEBUG',
            'propagate': True,
        },

    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

HUEY = {
    'backend': 'huey.backends.redis_backend',  # required.
    'name': 'hueytest',
    'connection': {'host': 'localhost', 'port': 6379},
    'always_eager': False,  # Defaults to False when running via manage.py run_huey
    # Options to pass into the consumer when running ``manage.py run_huey``
    'consumer_options': {'workers': 1, },
}

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

'''
The dictionary below contains group id's and school names.
These are the groups that are allowed to edit term informtion.
The school must be the same as the school_id in the school model.
'''


GUNICORN_CONFIG = 'gunicorn_local.py'
