from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.conf import settings
from braces.views import LoginRequiredMixin
from icommons_common.models import CourseInstance, SiteMap

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


class CourseIndexView(LoginRequiredMixin, DetailView):
    template_name = 'canvas_course_wizard/course.html'
    context_object_name = 'course'
    model = CourseInstance

    def is_current_user_member_of_course_staff(self, course_instance_id):
        staff_group = 'ScaleCourseStaff:%d' % course_instance_id
        user_groups = self.request.session.get('USER_GROUPS', [])
        return staff_group in user_groups

    def get_urls_from_course_instance_id(self, course_instance_id):
        '''
        check to see if there are any 'official' isites sites already setup for
        the given course instance id. There can be multiple official isites for a given course instance. 
        There can also be both and 'official' isite and canvas site. Canvas site urls are stored whole
        in the database in the external_id column of the course_site table. iSite keywords are also stored 
        in the same column of the same table. 
        '''

        # init a list to store the urls
        url_list = list()

        # try to select site_map records that correspond to the course_instance_id
        # of the selected course
        site_map = SiteMap.objects.filter(
            course_instance__course_instance_id=course_instance_id,
            map_type__map_type_id='official')

        if not site_map:
            return None
        else:
            for rec in site_map:
                # the site_type_id is 'isite' we need to build the url and append the keyword
                # if not, then we have a whole url for the external site so we can add it directly
                # to the list
                if rec.course_site.site_type_id == 'isite':
                    url_list.append(settings.COURSE_WIZARD.get(
                        'OLD_LMS_URL', None) + rec.course_site.external_id)
                else:
                    url_list.append(rec.course_site.external_id)

            # return the url_list with data
            return url_list

    def get_context_data(self, **kwargs):
        context = super(CourseIndexView, self).get_context_data(**kwargs)

        selected_course = self.object
        # check for existing isites or canvas courses, they will both be returned in the same list
        official_course_site_urls = self.get_urls_from_course_instance_id(selected_course.course_instance_id)
        user_is_course_staff = self.is_current_user_member_of_course_staff(selected_course.course_instance_id)
        # User can create a course if an official course site does not exist and if the user is a
        # member of the teaching staff
        user_can_create_course = user_is_course_staff and not official_course_site_urls

        context['user_can_create_course'] = user_can_create_course
        context['lms_course_urls'] = official_course_site_urls

        return context
