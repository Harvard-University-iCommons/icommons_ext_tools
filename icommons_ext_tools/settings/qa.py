
from .base import *

DEBUG = False

ALLOWED_HOSTS = ['termtool-qa.icommons.harvard.edu']

ICOMMONS_COMMON = {
    'ICOMMONS_API_HOST': 'https://isites.harvard.edu/services/',
    'ICOMMONS_API_USER': SECURE_SETTINGS.get('icommons_api_user', None),
    'ICOMMONS_API_PASS': SECURE_SETTINGS.get('icommons_api_pass', None),
}

CANVAS_WIZARD = {
    'TOKEN' : SECURE_SETTINGS.get('TOKEN', 'changeme'),
}

COURSE_WIZARD = {
    'OLD_LMS_URL' : SECURE_SETTINGS.get('OLD_LMS_URL', None),
}

QUALTRICS_LINK = {
    'AGREEMENT_ID' : SECURE_SETTINGS.get('qualtrics_agreement_id', None),
    'QUALTRICS_APP_KEY' : SECURE_SETTINGS.get('qualtrics_app_key', None),
    'QUALTRICS_API_URL' : SECURE_SETTINGS.get('qualtrics_api_url', None), 
    'QUALTRICS_API_USER' : SECURE_SETTINGS.get('qualtrics_api_user', None), 
    'QUALTRICS_API_TOKEN' : SECURE_SETTINGS.get('qualtrics_api_token', None), 
    'QUALTRICS_AUTH_GROUP' : SECURE_SETTINGS.get('qualtrics_auth_group', None),
    'USER_DECLINED_TERMS_URL' : 'ql:internal', # only in QA
    'USER_ACCEPTED_TERMS_URL' : 'ql:internal', # only in QA
}

CANVAS_SITE_SETTINGS = {
    'base_url': 'https://canvas.icommons.harvard.edu/',
}

CANVAS_SDK_SETTINGS = {
    'auth_token': SECURE_SETTINGS.get('canvas_token', None),
    'base_api_url': CANVAS_SITE_SETTINGS['base_url'] + 'api',
    'max_retries': 3,
    'per_page': 40,
}

DATABASE_ROUTERS = ['icommons_ext_tools.routers.DatabaseAppsRouter', ]

DATABASE_APPS_MAPPING = {
    'qualtrics_link': 'default',
}

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

# need to override the NLS_DATE_FORMAT that is set by oraclepool
'''
DATABASE_EXTRAS = {
    'session': ["ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS.FF'", ],
    'threaded': True,
}
'''

INSTALLED_APPS += ('gunicorn',)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

#CACHES = {
#    'default': {
#        'BACKEND': 'redis_cache.RedisCache',
#        'LOCATION': '127.0.0.1:6379',
#        'OPTIONS': {
#            'PARSER_CLASS': 'redis.connection.HiredisParser'
#        },
#    },
#}

#SESSION_ENGINE = 'redis_sessions.session'
#SESSION_REDIS_HOST = 'localhost'
#SESSION_REDIS_PORT = 6379
#SESSION_COOKIE_SECURE = True

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
            'filename': join(SITE_ROOT, 'logs/icommons_ext_tools.log'),
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
        'qualtrics_link': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'icommons_common': {
            'handlers': ['mail_admins', 'console', 'logfile'],
            'level': 'DEBUG',
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
        'icommons_common.auth.views': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
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


GUNICORN_CONFIG = 'gunicorn_qa.py'
