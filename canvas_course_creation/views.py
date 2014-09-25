from django.views.generic import View
from .controller import create_canvas_course
import logging

# import hashlib # Hash encrypt the user's HUID
# import json # Formats form post that user submitted to Piazza
# Get an instance of a logger
logger = logging.getLogger(__name__)


class CourseView(View):
    def get(self, request):
        pass

    def post(self, request):
        res = create_canvas_course(request.POST.get('course_sis_id'))
        pass
