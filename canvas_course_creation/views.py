from django.views.generic import View
from .controller import create_canvas_course
from django.views.decorators.http import require_http_methods
from django.shortcuts import render

import logging

# import hashlib # Hash encrypt the user's HUID
# import json # Formats form post that user submitted to Piazza
# Get an instance of a logger
logger = logging.getLogger(__name__)

@require_http_methods(['GET'])
def index(request, cid):
    print(" within index, invoked course_instance_id =%s" %(cid))
    course=create_canvas_course(cid)
    return render(request, 'index.html',{'course' : course})



class CourseView(View):
    def get(self, request):
        pass

    def post(self, request):
        course = create_canvas_course(request.POST.get('course_sis_id'))
        pass
