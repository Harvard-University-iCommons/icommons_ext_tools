from .base import *

# make tests faster
SOUTH_TESTS_MIGRATE = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
        'TEST_NAME': os.path.join(os.path.dirname(__file__), 'test.db'),
    },
}

ISITES_LMS_URL = ''

ICOMMONS_COMMON = {

    'ICOMMONS_API_HOST': 'https://qa.isites.harvard.edu/services/',
    'ICOMMONS_API_USER': SECURE_SETTINGS['icommons_api_user'],
    'ICOMMONS_API_PASS': SECURE_SETTINGS['icommons_api_pass'],
    'HARVARD_ACCOUNT_ID':'1',
}


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

CANVAS_SDK_SETTINGS = {
    'auth_token': SECURE_SETTINGS.get('canvas_token', None),
    'base_api_url': 'https://canvas.icommons.harvard.edu/api',
    'max_retries': 3,
    'per_page': 40,
}
