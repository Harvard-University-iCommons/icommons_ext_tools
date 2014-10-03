from .models_api import get_course_data
from .controller import create_canvas_course
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.http import Http404
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
import logging

# import hashlib # Hash encrypt the user's HUID
# import json # Formats form post that user submitted to Piazza
# Get an instance of a logger
logger = logging.getLogger(__name__)


@require_http_methods(['GET'])
def index(request):
    course = create_canvas_course(305841)
    return render(request, 'index.html', {'course': course})


class CourseDataMixin(object):
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        # Need a primary key for lookup of course data
        pk = kwargs.get(self.pk_url_kwarg, None)

        if pk is None:
            raise AttributeError("Course data mixin view %s must be called with "
                                 "an object pk."
                                 % self.__class__.__name__)

        self.course_data = self.get_course_data_object(pk)

        return super(CourseDataMixin, self).dispatch(request, *args, **kwargs)

    def get_course_data_object(self, pk):
        try:
            course_data = get_course_data(pk)
        except ObjectDoesNotExist as e:
            logger.error('Exception in create course: %s, exception=%s' % (pk, e))
            raise Http404(_("No %s found for the given key %s" % ('course_data', pk)))
        return course_data


class CanvasCourseSiteCreateView(CourseDataMixin, TemplateView):
    """
    Serves up the canvas course site creation wizard on GET and creates the
    course site on POST.
    """
    template_name = "canvas_course_creation/canvas_wizard.html"

    def post(self, request, *args, **kwargs):
        print self.course_data


class CanvasCourseSiteStatusView(TemplateView):
    pass
