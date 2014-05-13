from django.views.generic.base import TemplateView
from braces.views import LoginRequiredMixin
from icommons_common.models import CourseInstance
# from braces.views import CsrfExemptMixin
# from django.http import HttpResponse
import logging
from django.core.exceptions import ObjectDoesNotExist
# import hashlib # Hash encrypt the user's HUID
# import json # Formats form post that user submitted to Piazza
# Get an instance of a logger
logger = logging.getLogger(__name__)

# When setting up a tool in iSites, a POST request is initially made to the
# tool so we need to mark this entrypoint as exempt from the csrf requirement


class CourseWizardIndexView(LoginRequiredMixin, TemplateView):
    template_name = "canvas_course_wizard/index.html"


class CourseCatalogIndexView(TemplateView):
    template_name = 'canvas_course_wizard/course_catalog.html'

    def get_context_data(self, **kwargs):
        context = super(CourseCatalogIndexView, self).get_context_data(**kwargs)
        try:
            selected_course = CourseInstance.objects.get(
                course__registrar_code=self.kwargs.get('registrar_code', None),
                term__school_id=self.kwargs.get('school', None),
                term__academic_year=self.kwargs.get('year', None),
                term__term_code__term_name__startswith=self.kwargs.get('term', None)
            )
            context['course'] = selected_course
        except ObjectDoesNotExist:
            self.template_name = 'canvas_course_wizard/course_not_found.html'

        return context
