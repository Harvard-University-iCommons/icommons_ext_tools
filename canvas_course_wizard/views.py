from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from braces.views import LoginRequiredMixin
from icommons_common.models import CourseInstance, SiteMap
import re

# from braces.views import CsrfExemptMixin
# from django.http import HttpResponse
import logging

# import hashlib # Hash encrypt the user's HUID
# import json # Formats form post that user submitted to Piazza
# Get an instance of a logger
logger = logging.getLogger(__name__)

# When setting up a tool in iSites, a POST request is initially made to the
# tool so we need to mark this entrypoint as exempt from the csrf requirement


class CourseWizardIndexView(LoginRequiredMixin, TemplateView):
    template_name = "canvas_course_wizard/index.html"


class CourseIndexView(DetailView):
    template_name = 'canvas_course_wizard/course.html'
    context_object_name = 'course'
    model = CourseInstance

    def is_current_user_member_of_course_staff(self, course_instance_id):
        staff_group = 'ScaleCourseStaff:%d' % course_instance_id
        user_groups = self.request.session.get('USER_GROUPS', [])
        return staff_group in user_groups

    def get_existing_lms_urls_from_course_instance_id(self, selected_course):
        '''
        check to see if there are any 'official' isites sites already setup for
        the given course instance id. There can be multiple official isites for a given course instance. 
        There can also be both and 'official' isite and canvas site. Canvas site urls are stored whole
        in the database in the external_id column of the course_site table. iSite keywords are also stored 
        in the same column of the same table. 
        '''
        url_list = list()
        # try to select site_map records that correspond to the course_instance_id of the selected course
        site_map = SiteMap.objects.filter(
            course_instance__course_instance_id=selected_course.course_instance_id,
            map_type__map_type_id='official')

        if not site_map:
            return None
        else:
            for rec in site_map:
                # try to match an isite keyword ex: k680 or k123456
                # if there is a match, append the keyword to the isites url
                # and append the url to the url_list
                match_isite = re.match(r'(k\d{3,})', rec.course_site.external_id, re.M | re.I)
                if match_isite:
                    url_list.append(settings.COURSE_WIZARD.get(
                        'OLD_LMS_URL', None) + match_isite.group(1))

                # try to match a canvas course url, if there is a match append the url to the url_list
                match_canvas = re.match(
                    r'(https\:\/\/canvas\.harvard\.edu\/courses\/\d{3,})', rec.course_site.external_id, re.M | re.I)
                if match_canvas:
                    url_list.append(match_canvas.group(1))

            # return the url_list with data
            return url_list

        # if there were no items returned from the query return none
        return None

    def get_context_data(self, **kwargs):

        context = super(CourseIndexView, self).get_context_data(**kwargs)

        selected_course = self.object

        # check for existing isites or canvas courses, they will both be returned in the same list
        context['lms_course_urls'] = self.get_existing_lms_urls_from_course_instance_id(
            selected_course)

        # User can create a course if a canvas course does not already exist and
        # if the user is a  member of the teaching staff
        if not selected_course.canvas_course_id and self.is_current_user_member_of_course_staff(selected_course.course_instance_id):
            context['show_create'] = True
        else:
            context['show_create'] = False

        return context
