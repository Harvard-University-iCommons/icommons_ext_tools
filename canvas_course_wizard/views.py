from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin
from icommons_common.models import CourseInstance
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
        context = super(CourseIndexView, self).get_context_data(**kwargs)

        selected_course = self.object

        # User can create a course if a canvas course does not already exist and if the user is a  member of the teaching staff
        if not selected_course.canvas_course_id and self.is_current_user_member_of_course_staff(selected_course.course_instance_id):
            context['show_create'] = True
        else:
            context['show_create'] = False
            
        return context
        
