from .models import CourseData
from .models_api import get_course_data
#from canvas_sdk.methods.courses import create_new_course
from canvas_sdk.methods.sections import create_course_section
from django.conf import settings
from icommons_common.canvas_utils import SessionInactivityExpirationRC

import logging
import pprint

# Set up the request context that will be used for canvas API calls
SDK_CONTEXT = SessionInactivityExpirationRC(**settings.CANVAS_SDK_SETTINGS)
logger = logging.getLogger(__name__)

#This method creates a canvas course for the  sis_course_id provided.
def create_canvas_course(sis_course_id):

	result = None
	try:
		#1. fetch the course instance info 
				#Currently using  CourseInstance model: to be replaced by the Proxy model
		course_data = get_course_data(sis_course_id)
		if course_data:
			logger.debug(" \nobtained  course info for ci=%s, title=%s, section_name=%s"
			 %(course_data,course_data.short_title, course_data.main_section_name))
			result=course_data

			# #2. Create canvas course 
			# new_course = create_new_course(SDK_CONTEXT,
			# 		account_id=course_data.account_id,
			# 		course_name=course_data.course_name,
			# 		course_course_code=course_data.course_code, 
			# 		course_term_id=course_data.term_id,
			# 		course_sis_course_id=sis_course_id)
			
			# if new_course:

			#Temporarily reusing the course_data in place of new_course object
			# till the SDK call is fixed. The next 2 lines to be removed
			new_course= course_data
			new_course.id='5947'

			#3. Create course section after course  creation
			section = create_course_section(
		         		SDK_CONTEXT, 
		         		course_id=new_course.id,
		         		course_section_name=course_data.main_section_name,
		         		#course_section_sis_section_id=sis_course_id
		         		)
			logger.debug("\n created section")
		else:
			logger.error('No course record  found for %s sis_course_id!' %(sis_course_id) )
	except Exception as e:
			logger.error('Exception in  create course:  %s, exception=%s' % (sis_course_id, e))
			raise

	return result


