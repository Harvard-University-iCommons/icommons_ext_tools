# Django settings for icommons_ext_tools project.

import os
import logging
import time

from .secure import SECURE_SETTINGS


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Application definition

INSTALLED_APPS = [
    'django_cas_ng',
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

]

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'cached_auth.Middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'harvardkey_cas.backends.CASAuthBackend'
]

# CAS plugin attributes
CAS_SERVER_URL = SECURE_SETTINGS.get('cas_server_url', 'https://key-auth1-alb.iam.harvard.edu/cas/')
CAS_VERSION = 'CAS_2_SAML_1_0'
CAS_LOGGED_MSG = None
CAS_LOGIN_MSG = None

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
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': SECURE_SETTINGS.get('db_default_name', 'icommons_ext_tools'),
        'USER': SECURE_SETTINGS.get('db_default_user', 'postgres'),
        'PASSWORD': SECURE_SETTINGS.get('db_default_password'),
        'HOST': SECURE_SETTINGS.get('db_default_host', '127.0.0.1'),
        'PORT': SECURE_SETTINGS.get('db_default_port', 5432),  # Default postgres port
    },
    'coursemanager': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': SECURE_SETTINGS.get('db_coursemanager_name'),
        'USER': SECURE_SETTINGS.get('db_coursemanager_user'),
        'PASSWORD': SECURE_SETTINGS.get('db_coursemanager_password'),
        'HOST': SECURE_SETTINGS.get('db_coursemanager_host'),
        'PORT': str(SECURE_SETTINGS.get('db_coursemanager_port')),
        'CONN_MAX_AGE': 0,
    }
}

COURSE_SCHEMA_DB_NAME = 'coursemanager'
DATABASE_ROUTERS = ['icommons_common.routers.CourseSchemaDatabaseRouter']

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
TIME_ZONE = 'UTC'

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
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_ROOT = os.path.normpath(os.path.join(BASE_DIR, 'http_static'))

STATIC_URL = '/static/'

# Logging

# Turn off default Django logging
# https://docs.djangoproject.com/en/1.8/topics/logging/#disabling-logging-configuration
LOGGING_CONFIG = None

# Make sure log timestamps are in GMT
logging.Formatter.converter = time.gmtime


# Other app specific settings

QUALTRICS_LINK = {
    'AGREEMENT_ID': SECURE_SETTINGS.get('qualtrics_agreement_id'),
    'QUALTRICS_APP_KEY': SECURE_SETTINGS.get('qualtrics_app_key'),
    'QUALTRICS_API_URL': SECURE_SETTINGS.get('qualtrics_api_url'),
    'QUALTRICS_API_USER': SECURE_SETTINGS.get('qualtrics_api_user'),
    'QUALTRICS_API_TOKEN': SECURE_SETTINGS.get('qualtrics_api_token'),
    'QUALTRICS_AUTH_GROUP': SECURE_SETTINGS.get('qualtrics_auth_group'),
    'USER_DECLINED_TERMS_URL': SECURE_SETTINGS.get(
        'qualtrics_user_declined_terms_url',
        'http://surveytools.harvard.edu'),
    'USER_ACCEPTED_TERMS_URL': SECURE_SETTINGS.get(
        'qualtrics_user_accepted_terms_url'),
}
