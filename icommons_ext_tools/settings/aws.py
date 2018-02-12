from dj_log_config_helper import configure_installed_apps_logger

from .base import *

# tlt hostnames
ALLOWED_HOSTS = ['.tlt.harvard.edu']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = SECURE_SETTINGS['enable_debug']

# Make this unique and don't share with anybody!
SECRET_KEY = SECURE_SETTINGS['django_secret_key']

# AWS Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_USE_TLS = True
# Amazon Elastic Compute Cloud (Amazon EC2) throttles email traffic over port 25 by default.
# To avoid timeouts when sending email through the SMTP endpoint from EC2, use a different
# port (587 or 2587)
EMAIL_PORT = 587
EMAIL_HOST_USER = SECURE_SETTINGS.get('email_host_user', '')
EMAIL_HOST_PASSWORD = SECURE_SETTINGS.get('email_host_password', '')

# SSL is terminated at the ELB so look for this header to know that we should be in ssl mode
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True

# Log to file when running in aws
LOG_LEVEL = SECURE_SETTINGS['log_level']
LOG_FILE = os.path.join(
    SECURE_SETTINGS['log_root'], 'django-icommons_ext_tools.log')

configure_installed_apps_logger(
    LOG_LEVEL, verbose=True, filename=LOG_FILE)
