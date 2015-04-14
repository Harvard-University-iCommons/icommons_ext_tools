# Demo environment should be (nearly) identical to qa
from .qa import *

# sets 'from' email to show project and settings file name when sending emails to ADMINS
# SERVER_EMAIL_DISPLAY_NAME = '%s - %s' % (PROJECT_NAME, get_settings_file_name(__file__))
# SERVER_EMAIL = '%s <%s>' % (SERVER_EMAIL_DISPLAY_NAME, SERVER_EMAIL_EMAIL_ADDR)
