from icommons_common.models import CourseInstance
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
	logger.debug("sis id=%s" %sis_course_id)
	
	try:
		#1. fetch the course instance info 
				#Currently using  CourseInstance model: to be replaced by the Proxy model
		ci = CourseInstance.objects.get(course_instance_id=sis_course_id)
		if ci:
			logger.debug(" \nobtained  course info for ci=%s, title=%s, SDK Context=%s"
			 %(ci,ci.short_title,SDK_CONTEXT))
			result=ci

			# #2. Create canvas course 
			# new_course = create_new_course(SDK_CONTEXT,
			# 		account_id=ci.account_id,
			# 		course_name=ci.course_name,
			# 		course_course_code=ci.course_code, 
			# 		course_term_id=ci.term_id,
			# 		course_sis_course_id=sis_course_id)
			
			# if new_course:

			#Temporarily reusing the ci object til the SDK call is fixed. The next 2 lines to be removed
			new_course= ci
			new_course.id='5947'

			#3. Create course section after course  creation
			section = create_course_section(
		         		SDK_CONTEXT, 
		         		course_id=new_course.id,
		         		course_section_name=ci.short_title
		         		#course_section_name=ci.section_name
		         		#course_section_sis_section_id=sis_course_id
		         		)
			logger.debug("\n created section")

		   	# else : 
		   	# 	logger.error('Canvas course object is Null for sis_course_id=%s' %sis_course_id)
		else:
			logger.error('No course record  found for %s sis_course_id!' %(sis_course_id) )
	except Exception as e:
			logger.error('Exception in  create course:  %s, exception=%s' % (sis_course_id, e))
			raise

	return result


