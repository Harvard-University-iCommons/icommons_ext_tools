# Django settings for icommons_ext_tools project.

import os
import logging
import time

from django.core.urlresolvers import reverse_lazy
from .secure import SECURE_SETTINGS

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SECURE_SETTINGS.get('enable_debug', False)

# THESE ADDRESSES WILL RECEIVE EMAIL ABOUT CERTAIN ERRORS!
# Note: If this list (technically a tuple) has only one element, that
#       element must be followed by a comma for it to be processed
#       (cf section 3.2 of https://docs.python.org/2/reference/datamodel.html)
ADMINS = (
    ('iCommons Tech', 'icommons-technical@g.harvard.edu'),
)

MANAGERS = ADMINS

ENV_NAME = SECURE_SETTINGS.get('env_name', 'local')

# This is the address that admin emails (sent to the addresses in the ADMINS list) will be sent 'from'.
# It can be overridden in specific settings files to indicate what environment
# is producing admin emails (e.g. 'app env <email>').
SERVER_EMAIL_DISPLAY_NAME = 'icommons_ext_tools - %s' % ENV_NAME
SERVER_EMAIL = '%s <%s>' % (SERVER_EMAIL_DISPLAY_NAME, 'icommons-bounces@harvard.edu')

# Email subject prefix is what's shown at the beginning of the ADMINS email subject line
# Django's default is "[Django] ", which isn't helpful and wastes space in the subject line
# So this overrides the default and removes that unhelpful [Django] prefix.
# Specific settings files can override, for example to show the settings file being used:
# EMAIL_SUBJECT_PREFIX = '[%s] ' % SERVER_EMAIL_DISPLAY_NAME
# TLT-458: currently the tech_logger inserts its own hostname prefix if available, so this
#          is not being overridden in environment settings files at present.
EMAIL_SUBJECT_PREFIX = ''

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'icommons_common',
    # Adding monitor as an app so Django will
    # pick up templates with default enabled
    # app directories loader
    'icommons_common.monitor',
    'icommons_ui',
    'qualtrics_link',
    'canvas_course_site_wizard',
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

LOGIN_URL = reverse_lazy('pin:login')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Pull in 500.html page from base templates directory?
        'DIRS': [os.path.normpath(os.path.join(BASE_DIR, 'templates'))],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'icommons_common.auth.context_processors.pin_context',
            ],
        },
    },
]

ROOT_URLCONF = 'icommons_ext_tools.urls'

WSGI_APPLICATION = 'icommons_ext_tools.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

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

# Cache
# https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES

REDIS_HOST = SECURE_SETTINGS.get('redis_host', '127.0.0.1')
REDIS_PORT = SECURE_SETTINGS.get('redis_port', 6379)

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': "redis://%s:%s/0" % (REDIS_HOST, REDIS_PORT),
        'OPTIONS': {
            'PARSER_CLASS': 'redis.connection.HiredisParser'
        },
        # Provide a unique value for sharing cache among Django projects
        'KEY_PREFIX': 'icommons_ext_tools',
        # See following for default timeout (5 minutes as of 1.7):
        # https://docs.djangoproject.com/en/1.8/ref/settings/#std:setting-CACHES-TIMEOUT
        'TIMEOUT': SECURE_SETTINGS.get('default_cache_timeout_secs', 300),
    },
}

# SESSIONS (store in cache)

SESSION_COOKIE_AGE = 60 * 60 * 7

SESSION_COOKIE_NAME = 'djsessionid'

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'http_static'))

STATIC_URL = '/static/'

# Logging

# Turn off default Django logging
# https://docs.djangoproject.com/en/1.8/topics/logging/#disabling-logging-configuration
LOGGING_CONFIG = None

_DEFAULT_LOG_LEVEL = SECURE_SETTINGS.get('log_level', 'DEBUG')
# LOG_ROOT used for log file storage; EMAIL_FILE_PATH used for
# email output if EMAIL_BACKEND is filebased.EmailBackend
_LOG_ROOT = SECURE_SETTINGS.get('log_root', '')

# Make sure log timestamps are in GMT
logging.Formatter.converter = time.gmtime

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s\t%(asctime)s.%(msecs)03dZ\t%(name)s:%(lineno)s\t%(message)s',
            'datefmt': '%Y-%m-%dT%H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s\t%(name)s:%(lineno)s\t%(message)s',
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
        'default': {
            'class': 'logging.handlers.WatchedFileHandler',
            'level': _DEFAULT_LOG_LEVEL,
            'formatter': 'verbose',
            'filename': os.path.normpath(os.path.join(_LOG_ROOT, 'django-icommons_ext_tools.log')),
        },
        'console': {
            'level': _DEFAULT_LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'filters': ['require_debug_true'],
        },
    },
    # This is the default logger for any apps or libraries that use the logger
    # package, but are not represented in the `loggers` dict below.  A level
    # must be set and handlers defined.  Setting this logger is equivalent to
    # setting and empty string logger in the loggers dict below, but the separation
    # here is a bit more explicit.  See link for more details:
    # https://docs.python.org/2.7/library/logging.config.html#dictionary-schema-details
    'root': {
        'level': logging.WARNING,
        'handlers': ['default'],
    },
    'loggers': {
        'qualtrics_link': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['console', 'default'],
            'propagate': False,
        },
        'canvas_course_site_wizard': {
            'level': _DEFAULT_LOG_LEVEL,
            'handlers': ['default'],
            'propagate': False,
        },
    }
}

# Other app specific settings

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

# Used by canvas course site wizard

CANVAS_URL = SECURE_SETTINGS.get('canvas_url', 'https://changeme')

CANVAS_SITE_SETTINGS = {
    'base_url': CANVAS_URL + '/',
}

CANVAS_SDK_SETTINGS = {
    'auth_token': SECURE_SETTINGS.get('canvas_token'),  # Need a token
    'base_api_url': CANVAS_URL + '/api',
    'max_retries': 3,
    'per_page': 1000,
}

ISITES_LMS_URL = SECURE_SETTINGS.get('isites_lms_url', 'http://isites.harvard.edu/')

# Background task PID (lock) files
#   * If created in another directory, ensure the directory exists in runtime environment
PROCESS_ASYNC_JOBS_PID_FILE = 'process_async_jobs.pid'
FINALIZE_BULK_CREATE_JOBS_PID_FILE = 'finalize_bulk_create_jobs.pid'

BULK_COURSE_CREATION = {
    'log_long_running_jobs': True,
    'long_running_age_in_minutes': 30,
    'notification_email_subject': 'Sites created for {school} {term} term',
    'notification_email_body': 'Canvas course sites have been created for the '
                               '{school} {term} term.\n\n - {success_count} '
                               'course sites were created successfully.\n',
    'notification_email_body_failed_count': ' - {} course sites were not '
                                            'created.',
}

CANVAS_EMAIL_NOTIFICATION = {
    'from_email_address': 'icommons-bounces@harvard.edu',
    'support_email_address': 'tlt_support@harvard.edu',
    'course_migration_success_subject': 'Course site is ready',
    'course_migration_success_body': 'Success! \nYour new Canvas course site has been created and is ready for you at:\n'+
            ' {0} \n\n Here are some resources for getting started with your site:\n http://tlt.harvard.edu/getting-started#teachingstaff',

    'course_migration_failure_subject': 'Course site not created',
    'course_migration_failure_body': 'There was a problem creating your course site in Canvas.\n'+
            'Your local academic support staff has been notified and will be in touch with you.\n\n'+
            'If you have questions please contact them at:\n'+
            ' FAS: atg@fas.harvard.edu\n'+
            ' DCE/Summer: AcademicTechnology@dce.harvard.edu\n'+
            ' (Let them know that course site creation failed for sis_course_id: {0} ',

    'support_email_subject_on_failure': 'Course site not created',
    'support_email_body_on_failure': 'There was a problem creating a course site in Canvas via the wizard.\n\n'+
            'Course site creation failed for sis_course_id: {0}\n'+
            'User: {1}\n'+
            '{2}\n'+
            'Environment: {3}\n',
    'environment': ENV_NAME.capitalize(),
}
