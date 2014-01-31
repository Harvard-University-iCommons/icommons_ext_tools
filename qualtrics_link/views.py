

from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.http import require_http_methods
#from ims_lti_py.tool_provider import DjangoToolProvider
from time import time
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
import json
import re
from django.conf import settings
from django.template import RequestContext
#from icommons_common.models import CourseInstance
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#from ims_lti_py.tool_config import ToolConfig

import logging

logger = logging.getLogger(__name__)


# Create your views here.
from django.core.urlresolvers import reverse

from django.views import generic
from django.contrib import messages

#from icommons_common.models import School, Term
#from icommons_common.auth.views import LoginRequiredMixin
#from term_tool.forms import EditTermForm, CreateTermForm

from django.conf import settings

import logging

#from util import util

logger = logging.getLogger(__name__)


@require_http_methods(['GET'])
def index(request):
    logger.info("request to index.")
    return render(request, 'qualtrics_link/index.html')

@login_required
@require_http_methods(['GET'])
def launch(request):

    #if request.user.is_authenticated():
        # pull some params from the LTI launch request and store them in the session
        #for key, value in request.POST.iteritems():
        #    logger.debug('%s: %s' % (key, value))

        # then redirect the user to the main view
    logger.debug("redirect user to the first page")

    return render(request, 'qualtrics_link/main.html', {'request': request })

    #else:
    #    return render(request, 'qualtrics_link/error.html', {'message': 'Error: user is not authenticated!'})


#@login_required
@require_http_methods(['GET'])
def main(request):

	logger.debug('Now in main')
	return render(request, 'qualtrics_link/main.html', {'request': request })





    