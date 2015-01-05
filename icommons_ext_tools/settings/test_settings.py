from .base import *

# ensures mail won't be sent by unit tests
ADMINS = ()
MANAGERS = ADMINS

# make tests faster
SOUTH_TESTS_MIGRATE = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(dirname(__file__), 'test.db'),
        'TEST_NAME': join(dirname(__file__), 'test.db'),
    },
}

ISITES_LMS_URL = ''

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

CANVAS_EMAIL_NOTIFICATION = {
    'from_email_address'    : 'icommons-bounces@harvard.edu',
    'support_email_address' : 'tlt_support@harvard.edu',
    'course_migration_success_subject'  : 'Course site is ready : (TEST, PLEASE IGNORE)',
    'course_migration_success_body'     : 'Success! \nYour new Canvas course site has been created and is ready for you at:\n'+
            ' {0} \n\n Here are some resources for getting started with your site:\n http://tlt.harvard.edu/getting-started#teachingstaff',
    'course_migration_failure_subject'  : 'Course site not created (TEST, PLEASE IGNORE) ',
    'course_migration_failure_body'     : 'There was a problem creating your course site in Canvas.\n'+
            'Your local academic support staff has been notified and will be in touch with you.\n\n'+
            'If you have questions please contact them at:\n'+
            ' FAS: atg@fas.harvard.edu\n'+
            ' DCE: academictechnology@dce.harvard.edu\n'+
            ' (Let them know that course site creation failed for sis_course_id: {0} ',
    'support_email_subject_on_failure'  : 'TLT: Course site not created (TEST, PLEASE IGNORE) ',
    'support_email_body_on_failure'     : 'There was a problem creating a course site in Canvas via the wizard.\n\n'+
            'Course site creation failed for sis_course_id: {0}\n'+
            'User: {1}\n'+
            '{2}\n'+
            'Environment: Test\n',
}
