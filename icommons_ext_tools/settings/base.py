# Django settings for icommons_ext_tools project.

from . import get_settings_file_name
from .secure import SECURE_SETTINGS
from os.path import abspath, basename, dirname, join, normpath
from sys import path
from django.core.urlresolvers import reverse_lazy

### Path stuff as recommended by Two Scoops / with local mods

# Absolute filesystem path to the Django project config directory:
# (this is the parent of the directory where this file resides,
# since this file is now inside a 'settings' pacakge directory)
DJANGO_PROJECT_CONFIG = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
# (this is one directory up from the project config directory)
SITE_ROOT = dirname(DJANGO_PROJECT_CONFIG)

# Site name:
SITE_NAME = basename(SITE_ROOT)

# Name of project (which settings apply to)
PROJECT_NAME = basename(DJANGO_PROJECT_CONFIG)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(SITE_ROOT)

### End path stuff

# THESE ADDRESSES WILL RECEIVE EMAIL ABOUT CERTAIN ERRORS!
# Note: If this list (technically a tuple) has only one element, that
#       element must be followed by a comma for it to be processed
#       (cf section 3.2 of https://docs.python.org/2/reference/datamodel.html)
ADMINS = (
    ('iCommons Tech', 'icommons-technical@g.harvard.edu'),
)

# LOG_ROOT used for log file storage; EMAIL_FILE_PATH used for
# email output if EMAIL_BACKEND is filebased.EmailBackend
LOG_ROOT = SECURE_SETTINGS.get('log_root', 'logs/')

# This is the address that admin emails (sent to the addresses in the ADMINS list) will be sent 'from'.
# It can be overridden in specific settings files to indicate what environment
# is producing admin emails (e.g. 'app env <email>').
SERVER_EMAIL_DISPLAY_NAME = '%s - %s' % (DJANGO_PROJECT_CONFIG, SECURE_SETTINGS.get('env_name', 'production'))
SERVER_EMAIL = '%s <%s>' % (SERVER_EMAIL_DISPLAY_NAME, 'icommons-bounces@harvard.edu')

# Email subject prefix is what's shown at the beginning of the ADMINS email subject line
# Django's default is "[Django] ", which isn't helpful and wastes space in the subject line
# So this overrides the default and removes that unhelpful [Django] prefix.
# Specific settings files can override, for example to show the settings file being used:
# EMAIL_SUBJECT_PREFIX = '[%s] ' % SERVER_EMAIL_DISPLAY_NAME
# TLT-458: currently the tech_logger inserts its own hostname prefix if available, so this
#          is not being overridden in environment settings files at present.
EMAIL_SUBJECT_PREFIX = ''

# Use filebased.EmailBackend with EMAIL_FILE_PATH for verifying email format
# and submission without generating actual SMTP requests
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# If using filebased.EmailBackend, override EMAIL_FILE_PATH in individual
# environment settings files to point to the environment-specific log directory.
# Here in the base settings it's set explicitly to None so it will throw an
# Exception unless overridden in individual environment settings
EMAIL_FILE_PATH = LOG_ROOT

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

MANAGERS = ADMINS

# DATABASES are defined in individual environment settings

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# STATIC_ROOT can be overriden in individual environment settings
STATIC_ROOT = normpath(join(SITE_ROOT, 'http_static'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/ext_tools/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #normpath(join(SITE_ROOT, 'static')),
)


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = SECURE_SETTINGS.get('django_secret_key', 'changeme')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    #'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cached_auth.Middleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',

)

AUTHENTICATION_BACKENDS = (
    'icommons_common.auth.backends.PINAuthBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "icommons_common.auth.context_processors.pin_context",
)

ROOT_URLCONF = 'icommons_ext_tools.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'icommons_ext_tools.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    normpath(join(SITE_ROOT, 'templates')),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.webdesign',
    # Uncomment the next line to enable the admin:
    #'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'icommons_common',
    'icommons_common.monitor',
    'icommons_ui',
    'qualtrics_link',
    'crispy_forms',
    'canvas_course_site_wizard',
)

# session cookie lasts for 7 hours (in seconds)
SESSION_COOKIE_AGE = 60 * 60 * 7

SESSION_COOKIE_NAME = 'djsessionid'

SESSION_COOKIE_HTTPONLY = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CRISPY_TEMPLATE_PACK = 'bootstrap3'

LOGIN_URL = reverse_lazy('pin:login')

ICOMMONS_COMMON = {
    'ICOMMONS_API_HOST': SECURE_SETTINGS.get('icommons_api_host'),
    'ICOMMONS_API_USER': SECURE_SETTINGS.get('icommons_api_user'),
    'ICOMMONS_API_PASS': SECURE_SETTINGS.get('icommons_api_pass'),
}

# Important this be declared, but we need to allow for unit tests to run in a Jenkins environment so
# default to a bogus url.
CANVAS_URL = SECURE_SETTINGS.get('canvas_url', 'https://changeme')

COURSE_WIZARD = {
    'TERM_TOOL_BASE_URL' : 'https://isites.harvard.edu',
}

CANVAS_SITE_SETTINGS = {
    'base_url': CANVAS_URL + '/',
}

CANVAS_SDK_SETTINGS = {
    'auth_token': SECURE_SETTINGS.get('canvas_token'),  # Need a token
    'base_api_url': CANVAS_URL + '/api',
    'max_retries': 3,
    'per_page': 1000,
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
    'environment' : 'Production',
}

BULK_COURSE_CREATION = {
    'log_long_running_jobs': True,
    'long_running_age_in_minutes': 30,
    'notification_email_subject': 'Finished creating {} courses in term {}',
    'notification_email_body': 'We finished running the process to create course sites '
                               'at the school {} for the term {} \n\n'
                               ' - {} course sites were created successfully.\n',
    'notification_email_body_failed_count': ' - {} course sites were not created.',
}

# Background task PID (lock) files
#   * If created in another directory, ensure the directory exists in runtime environment
PROCESS_ASYNC_JOBS_PID_FILE = 'process_async_jobs.pid'
FINALIZE_BULK_CREATE_JOBS_PID_FILE = 'finalize_bulk_create_jobs.pid'

QUALTRICS_LINK = {
    'AGREEMENT_ID': SECURE_SETTINGS.get('qualtrics_agreement_id'),
    'QUALTRICS_APP_KEY': SECURE_SETTINGS.get('qualtrics_app_key'),
    'QUALTRICS_API_URL': SECURE_SETTINGS.get('qualtrics_api_url'),
    'QUALTRICS_API_USER': SECURE_SETTINGS.get('qualtrics_api_user'),
    'QUALTRICS_API_TOKEN': SECURE_SETTINGS.get('qualtrics_api_token'),
    'QUALTRICS_AUTH_GROUP': SECURE_SETTINGS.get('qualtrics_auth_group'),
    'USER_DECLINED_TERMS_URL': 'ql:internal',
    'USER_ACCEPTED_TERMS_URL': 'ql:internal',
}
