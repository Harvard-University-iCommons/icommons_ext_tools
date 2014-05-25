from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
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
 

class CourseIndexView(DetailView):
    template_name = 'canvas_course_wizard/course.html'
    context_object_name = 'course'
    model = CourseInstance

    def is_current_user_member_of_course_staff(self, course_instance_id):
        staff_group = 'ScaleCourseStaff:%d' % course_instance_id
        user_groups = self.request.session.get('USER_GROUPS', [])
        return staff_group in user_groups


    def get_context_data(self, **kwargs):
        """ 
        given a course_instance_id determine if an isite exists. 
        If one does, return the url to the isite. If no, return false.
        test id for dev 76592 has no iSite, id 21114 has an isite, id 298211 has both 
        a canvas site and an isite

        given a course_instance_id determine if a canvas site already exists. 
        If one does, return the url to the site. If no, return false.
        test id for dev 76592 has no iSite, id 21114 has an isite, id 298211 has both 
        a canvas site and an isite    
        """

        context = super(CourseIndexView, self).get_context_data(**kwargs)

        selected_course = self.object
        isites_urls = list()
        context['isite_course_url'] = None

        site_map = SiteMap.objects.filter(course_instance__course_instance_id=selected_course.course_instance_id, map_type__map_type_id='official')
        #print '###############'+str(site_map)
        #print '<<<<<<<<<<<<<<<'+str(site_map[0])
        if site_map:
            for rec in site_map:
                isites_urls.append(settings.COURSE_WIZARD.get('OLD_LMS_URL', None)+rec.course_site.external_id)
            context['isite_course_url'] = isites_urls


        #if len(site_map) > 0:
        #    context['isite_course_url'] = settings.COURSE_WIZARD.get('OLD_LMS_URL', None)+site_map[0].course_site.external_id
        #else:
        #    context['isite_course_url'] = None

        # try:
        #     site_map = SiteMap.objects.get(course_instance__course_instance_id=selected_course.course_instance_id, map_type__map_type_id='official')
    
        #     context['isite_course_url'] = settings.COURSE_WIZARD.get('OLD_LMS_URL', None)+site_map.course_site.external_id
        #     #print context['isite_course_url']
        #     #print '>>>>>>ok<<<<<<<<'
        # except SiteMap.DoesNotExist:
        #     print '>>>>>>>>>>>>> the SiteMap.DoesNotExist exception was thrown'
        #     context['isite_course_url'] = None



        if selected_course.canvas_course_id:
            context['canvas_course_url'] = settings.COURSE_WIZARD.get('CANVAS_SERVER_BASE_URL', None) + 'courses/' + str(selected_course.canvas_course_id)
        else:
            context['canvas_course_url'] = None

        # User can create a course if a canvas course does not already exist and
        # if the user is a  member of the teaching staff
        if not selected_course.canvas_course_id and self.is_current_user_member_of_course_staff(selected_course.course_instance_id):
            context['show_create'] = True
        else:
            context['show_create'] = False

        return context
