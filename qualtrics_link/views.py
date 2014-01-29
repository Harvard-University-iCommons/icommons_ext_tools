from django.shortcuts import render

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
