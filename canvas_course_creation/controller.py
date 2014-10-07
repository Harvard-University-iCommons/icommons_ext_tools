from .models_api import get_course_data
from canvas_sdk.methods.courses import create_new_course
from canvas_sdk.methods.sections import create_course_section
from django.conf import settings
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from icommons_common.canvas_utils import SessionInactivityExpirationRC

import logging
import pprint

# Set up the request context that will be used for canvas API calls
SDK_CONTEXT = SessionInactivityExpirationRC(**settings.CANVAS_SDK_SETTINGS)
logger = logging.getLogger(__name__)

def create_canvas_course(sis_course_id):
	"""This method creates a canvas course for the  sis_course_id provided."""

	new_course = None
	try:
		#1. fetch the course instance info 
		course_data = get_course_data(sis_course_id)

		logger.info("\n obtained  course info for ci=%s, acct_id=%s, course_name=%s, code=%s, term=%s, section_name=%s\n"
		 %(course_data,course_data.sis_account_id, course_data.course_name, course_data.course_code, course_data.sis_term_id,course_data.primary_section_name() ))
	except ObjectDoesNotExist as e:
		logger.error('ObjectDoesNotExist  exception in  create course:  %s, exception=%s' % (sis_course_id, e))
		raise Http404

	#2. Create canvas course
	new_course = create_new_course(SDK_CONTEXT,
			account_id = 'sis_account_id:' + course_data.sis_account_id,
			course_name = course_data.course_name,
			course_course_code = course_data.course_code,
			course_term_id = 'sis_term_id:' + course_data.sis_term_id,
			course_sis_course_id= sis_course_id).json()
	logger.info("created  course object, ret=%s" % (new_course))

	# 3. Create course section after course  creation
	section = create_course_section(
				SDK_CONTEXT, 
				course_id = new_course['id'],
         		course_section_name = course_data.primary_section_name(),
         		course_section_sis_section_id = sis_course_id
         		)
	logger.info("created section= %s" %(section.json()))

	return new_course
