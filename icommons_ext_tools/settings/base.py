# Django settings for icommons_ext_tools project.

from .secure import SECURE_SETTINGS
from os.path import abspath, dirname, join, normpath
from django.core.urlresolvers import reverse_lazy

ALLOWED_HOSTS = ['*']

# Absolute filesystem path to the Django project config directory:
# (this is the parent of the directory where this file resides,
# since this file is now inside a 'settings' pacakge directory)
BASE_DIR = dirname(dirname(abspath(__file__)))

DEBUG = SECURE_SETTINGS.get('enable_debug', False)

CRISPY_FAIL_SILENTLY = not DEBUG

# Make this unique, and don't share it with anybody.
SECRET_KEY = SECURE_SETTINGS.get('django_secret_key', 'changeme')

# THESE ADDRESSES WILL RECEIVE EMAIL ABOUT CERTAIN ERRORS!
# Note: If this list (technically a tuple) has only one element, that
#       element must be followed by a comma for it to be processed
#       (cf section 3.2 of https://docs.python.org/2/reference/datamodel.html)
ADMINS = (
    ('iCommons Tech', 'icommons-technical@g.harvard.edu'),
)

MANAGERS = ADMINS

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'icommons_common',
    'icommons_ui',
    'qualtrics_link',
    'crispy_forms',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'cached_auth.Middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'icommons_common.auth.backends.PINAuthBackend',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Pull in 500.html page from base templates directory?
        'DIRS': [normpath(join(BASE_DIR, 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'icommons_common.auth.context_processors.pin_context',
            ],
            'debug': DEBUG,
        },
    },
]

ROOT_URLCONF = 'icommons_ext_tools.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'icommons_ext_tools.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': SECURE_SETTINGS.get('django_db', None),
        'USER': SECURE_SETTINGS.get('django_db_user', None),
        'PASSWORD': SECURE_SETTINGS.get('django_db_pass', None),
        'HOST': SECURE_SETTINGS.get('django_db_host', None),
        'PORT': str(SECURE_SETTINGS.get('django_db_port', None)),
        'OPTIONS': {
            'threaded': True,
        },
        'CONN_MAX_AGE': 1200,
    }
}

DATABASE_ROUTERS = ['icommons_common.routers.DatabaseAppsRouter']
DATABASE_APPS_MAPPING = {}
DATABASE_MIGRATION_WHITELIST = ['default']

LOGIN_URL = reverse_lazy('pin:login')

# SESSIONS (store in cache)

# session cookie lasts for 7 hours (in seconds)
SESSION_COOKIE_AGE = 60 * 60 * 7

SESSION_COOKIE_NAME = 'djsessionid'

SESSION_COOKIE_HTTPONLY = True

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# CACHE

REDIS_HOST = SECURE_SETTINGS.get('redis_host', '127.0.0.1')
REDIS_PORT = SECURE_SETTINGS.get('redis_port', 6379)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': "%s:%s" % (REDIS_HOST, REDIS_PORT),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
        'TIMEOUT': SESSION_COOKIE_AGE,  # Tie default timeout to session cookie age
        # Provide a unique value for sharing cache among Django projects
        'KEY_PREFIX': 'icommons_ext_tools',
    },
}

# EMAIL Settings


# This is the address that admin emails (sent to the addresses in the ADMINS list) will be sent 'from'.
# It can be overridden in specific settings files to indicate what environment
# is producing admin emails (e.g. 'app env <email>').
SERVER_EMAIL_DISPLAY_NAME = '%s - %s' % (BASE_DIR, SECURE_SETTINGS.get('env_name', 'production'))
SERVER_EMAIL = '%s <%s>' % (SERVER_EMAIL_DISPLAY_NAME, 'icommons-bounces@harvard.edu')

# Email subject prefix is what's shown at the beginning of the ADMINS email subject line
# Django's default is "[Django] ", which isn't helpful and wastes space in the subject line
# So this overrides the default and removes that unhelpful [Django] prefix.
# Specific settings files can override, for example to show the settings file being used:
# EMAIL_SUBJECT_PREFIX = '[%s] ' % SERVER_EMAIL_DISPLAY_NAME
# TLT-458: currently the tech_logger inserts its own hostname prefix if available, so this
#          is not being overridden in environment settings files at present.
EMAIL_SUBJECT_PREFIX = ''

# Use smtp.EmailBackend with EMAIL_HOST and EMAIL_USE_TLS
# to send actual mail via SMTP
# Note that if DEBUG = True, emails will not be sent by the ADMINS email handler
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = SECURE_SETTINGS.get('email_host', 'mailhost.harvard.edu')
EMAIL_HOST_USER = SECURE_SETTINGS.get('email_host_user', '')
EMAIL_HOST_PASSWORD = SECURE_SETTINGS.get('email_host_password', '')
EMAIL_USE_TLS = SECURE_SETTINGS.get('email_use_tls', False)
# EMAIL_PORT for use in AWS environment
# (see http://docs.aws.amazon.com/ses/latest/DeveloperGuide/smtp-connect.html)
EMAIL_PORT = SECURE_SETTINGS.get('email_port', 25)


# DATABASES

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': SECURE_SETTINGS.get('django_db'),
        'USER': SECURE_SETTINGS.get('django_db_user'),
        'PASSWORD': SECURE_SETTINGS.get('django_db_pass'),
        'HOST': SECURE_SETTINGS.get('django_db_host'),
        'PORT': str(SECURE_SETTINGS.get('django_db_port')),
        'OPTIONS': {
            'threaded': True,
        },
        'CONN_MAX_AGE': 0,
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
# NOTE: Django 1.7+ project template defaults to UTC time.  This should
# help Splunk logs.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# STATIC_ROOT can be overriden in individual environment settings
STATIC_ROOT = normpath(join(BASE_DIR, 'http_static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/ext_tools/static/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'

ICOMMONS_COMMON = {
    'ICOMMONS_API_HOST': SECURE_SETTINGS.get('icommons_api_host'),
    'ICOMMONS_API_USER': SECURE_SETTINGS.get('icommons_api_user'),
    'ICOMMONS_API_PASS': SECURE_SETTINGS.get('icommons_api_pass'),
}

QUALTRICS_LINK = {
    'AGREEMENT_ID': SECURE_SETTINGS.get('qualtrics_agreement_id'),
    'QUALTRICS_APP_KEY': SECURE_SETTINGS.get('qualtrics_app_key'),
    'QUALTRICS_API_URL': SECURE_SETTINGS.get('qualtrics_api_url'),
    'QUALTRICS_API_USER': SECURE_SETTINGS.get('qualtrics_api_user'),
    'QUALTRICS_API_TOKEN': SECURE_SETTINGS.get('qualtrics_api_token'),
    'QUALTRICS_AUTH_GROUP': SECURE_SETTINGS.get('qualtrics_auth_group'),
    'USER_DECLINED_TERMS_URL': SECURE_SETTINGS.get('qualtrics_user_declined_terms_url'),
    'USER_ACCEPTED_TERMS_URL': SECURE_SETTINGS.get('qualtrics_user_accepted_terms_url'),
}

_DEFAULT_LOG_LEVEL = SECURE_SETTINGS.get('log_level', 'DEBUG')
# LOG_ROOT used for log file storage; EMAIL_FILE_PATH used for
# email output if EMAIL_BACKEND is filebased.EmailBackend
_LOG_ROOT = SECURE_SETTINGS.get('log_root', '')

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
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
        'logfile': {
            'level': _DEFAULT_LOG_LEVEL,
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': normpath(join(_LOG_ROOT, 'django-icommons_ext_tools.log')),
            'formatter': 'verbose',
        },
        'jobs-logfile': {
            'level': _DEFAULT_LOG_LEVEL,
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': normpath(join(_LOG_ROOT, 'django-jobs-icommons_ext_tools.log')),
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'qualtrics_link': {
            'handlers': ['console', 'mail_admins', 'logfile'],
            'level': 'DEBUG',
        },
        'icommons_common': {
            'handlers': ['mail_admins', 'console', 'logfile'],
            'level': 'DEBUG',
        },
        'icommons_ui': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
        # Apps can log to tech_mail to selectively send ERROR emails to ADMINS
        'tech_mail': {
            'handlers': ['mail_admins', 'console', 'logfile'],
            'level': 'ERROR',
        },
        'oraclepool': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}
