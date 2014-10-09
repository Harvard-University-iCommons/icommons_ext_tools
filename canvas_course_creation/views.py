from .controller import create_canvas_course
from .mixins import CourseSiteCreationAllowedMixin
from braces.views import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)


class CanvasCourseSiteCreateView(LoginRequiredMixin, CourseSiteCreationAllowedMixin, TemplateView):
    """
    Serves up the canvas course site creation wizard on GET and creates the
    course site on POST.
    """
    template_name = "canvas_course_creation/canvas_wizard.html"

    def post(self, request, *args, **kwargs):
        course = create_canvas_course(self.object.pk)
        # Temporary redirect based on newly created course id, will eventually be async job id
        return redirect('ccsw-status', course['id'])


class CanvasCourseSiteStatusView(LoginRequiredMixin, TemplateView):
    """ Displays status of async job for template copy """
    template_name = "canvas_course_creation/status.html"
