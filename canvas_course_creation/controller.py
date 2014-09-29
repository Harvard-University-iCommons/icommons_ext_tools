from .models_api import get_course_data
from canvas_sdk.methods.courses import create_new_course
from canvas_sdk.methods.sections import create_course_section
from django.conf import settings
from django.http import Http404
from icommons_common.canvas_utils import SessionInactivityExpirationRC

import logging
import pprint

# Set up the request context that will be used for canvas API calls
SDK_CONTEXT = SessionInactivityExpirationRC(**settings.CANVAS_SDK_SETTINGS)
logger = logging.getLogger(__name__)

def create_canvas_course(sis_course_id):
	"""This method creates a canvas course for the  sis_course_id provided."""


	result = None
	try:
		#1. fetch the course instance info 
		course_data = get_course_data(sis_course_id)

		logger.debug("obtained  course info for ci=%s, acct_id=%s, title=%s, course_name=%s, code=%s, term=%s\n\n"
		 %(course_data,course_data.account_id(), course_data.short_title, course_data.course_name(), course_data.course_code(), course_data.meta_term_id(), ))
	except ObjectDoesNotExist as e:
		logger.error('Exception in  create course:  %s, exception=%s' % (sis_course_id, e))
		raise Http404

	result=course_data

	# #2. Create canvas course 
	# new_course = create_new_course(SDK_CONTEXT,
	# 		account_id=course_data.account_id,
	# 		#course_name=course_data.course_name(),
	# 		#course_course_code=course_data.course_code(),
	# 		#course_term_id=course_data.meta_term_id(),
	# 		#course_sis_course_id=sis_course_id)
	#logger.debug(" \n\n\n created  course object, ret=%s" % (new_course))
		

	#Temporarily reusing the course_data in place of new_course object
	# till the SDK call is fixed. The next 2 lines to be removed
	new_course= course_data
	new_course.id='5947'

	#3. Create course section after course  creation
	section = create_course_section(
         		SDK_CONTEXT, 
         		course_id=new_course.id,
         		course_section_name=course_data.main_section_name()
         		#course_section_sis_section_id=sis_course_id
         		)
	logger.debug("\n created section")
		
	

	return result


