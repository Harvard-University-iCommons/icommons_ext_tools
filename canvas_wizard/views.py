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
    logger.info('Launch view')
    return render(request, 'canvas_wizard/launch.html')

@login_required
@require_http_methods(['GET'])
def select_course(request):
    """
    doc string
    """
    logger.info('select course view')
    return render(request, 'canvas_wizard/select_course.html')

@login_required
@require_http_methods(['GET'])
def select_template_or_course(request):
    """
    doc string
    """
    logger.info('select course view')
    return render(request, 'canvas_wizard/select_template_or_course.html')

@login_required
@require_http_methods(['GET'])
def select_isite_import(request):
    """
    doc string
    """
    logger.info('select course view')
    return render(request, 'canvas_wizard/select_isite_import.html')

@login_required
@require_http_methods(['GET'])
def finish(request):
    """
    doc string
    """
    logger.info('select course view')
    return render(request, 'canvas_wizard/finish.html')











