from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from icommons_common.monitor.views import BaseMonitorResponseView
from icommons_common.models import QualtricsAccessList
from icommons_common.icommonsapi import IcommonsApi
from icommons_common.auth.decorators import group_membership_restriction
from django.http import HttpResponse
from datetime import date
import time
import datetime
import urllib
import pprint

from canvas_api import Canvasapi

logger = logging.getLogger(__name__)

class MonitorResponseView(BaseMonitorResponseView):
    def healthy(self):
        return True

@login_required
@require_http_methods(['GET'])
def index(request):
    """
    doc string
    """
    logger.info('Launch view')
    return render(request, 'canvas_wizard/index.html')

@login_required
@require_http_methods(['GET'])
def launch(request):
    """
    doc string
    """
    instance = Canvasapi()
    #pp = pprint.PrettyPrinter(indent=4)
    huid = request.user.username
    #pp.pprint(request)
    logger.info('Launch view')
    return render(request, 'canvas_wizard/launch.html', {'huid': huid})

@login_required
@require_http_methods(['GET'])
def select_course(request):
    """
    doc string
    """
    if 'course_id' in request.session:
        del request.session['course_id']

    if 'template_id' in request.session:
        del request.session['template_id']
    
    if 'isite_site_id' in request.session:
        del request.session['isite_site_id']

    # get course data for user to select which course they want to create in Canvas
    # make sure the course does not already exist in Canvas 

    # course data comes from the course instance table

    logger.info('select course view')
    return render(request, 'canvas_wizard/select_course.html')

@login_required
@require_http_methods(['GET'])
def select_template_or_course(request):
    """
    doc string
    """

    if 'course' in request.GET:
        course_id = request.GET['course']
        request.session['course_id'] = course_id

    return render(request, 'canvas_wizard/select_template_or_course.html', {'session' : request.session})

@login_required
@require_http_methods(['GET'])
def select_isite_import(request):
    """
    doc string
    """
    if 'template' in request.GET:
        template_id = request.GET['template']
        request.session['template_id'] = template_id

    return render(request, 'canvas_wizard/select_isite_import.html', {'session' : request.session})

@login_required
@require_http_methods(['GET'])
def finish(request):
    """
    doc string
    """
    if 'isite_site_id' in request.GET:
        isite_site_id = request.GET['isite_site_id']
        request.session['isite_site_id'] = isite_site_id

    # here we will initiate the course copy and isites import
    # instance.create_course_content_migration(source_course_id, course_id)

    logger.info('select course view')
    return render(request, 'canvas_wizard/finish.html', {'session' : request.session})











