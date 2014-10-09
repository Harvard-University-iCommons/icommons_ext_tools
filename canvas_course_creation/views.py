from .controller import create_canvas_course
from .mixins import CourseDataMixin
from braces.views import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)


class CanvasCourseSiteCreateView(LoginRequiredMixin, CourseDataMixin, TemplateView):
    """
    Serves up the canvas course site creation wizard on GET and creates the
    course site on POST.
    """
    template_name = "canvas_course_creation/canvas_wizard.html"

    def dispatch(self, request, *args, **kwargs):
        self.course_data = self.get_object()
        return super(CanvasCourseSiteCreateView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        course = create_canvas_course(self.course_data.pk)
        # Temporary redirect based on newly created course id, will eventually be async job id
        return redirect('ccsw-status', course['id'])


class CanvasCourseSiteStatusView(LoginRequiredMixin, TemplateView):
    """ Displays status of async job for template copy """
    template_name = "canvas_course_creation/status.html"
