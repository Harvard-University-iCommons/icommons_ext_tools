

from django.shortcuts import render, render_to_response, redirect
from django.views.decorators.http import require_http_methods
from time import time
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl
import json
import re
from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from icommons_common.monitor.views import BaseMonitorResponseView
from icommons_common.models import QualtricsAccessList
from django.http import HttpResponse
from django.views import generic
from django.contrib import messages
import time
import datetime
from datetime import date
import hashlib
import hmac
from Crypto import Random
from Crypto.Cipher import AES
import base64
import requests 
import urllib
from django.conf import settings
import logging

import pprint

from qualtrics_link.icommonsapi import IcommonsApi
from qualtrics_link.util import *
from qualtrics_link.forms import SpoofForm

#from util import util

logger = logging.getLogger(__name__)


class MonitorResponseView(BaseMonitorResponseView):
    def healthy(self):
        return True

#BLOCK_SIZE=16
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]




@require_http_methods(['GET'])
def index(request):
    return render(request, 'qualtrics_link/index.html')

@login_required
@require_http_methods(['GET'])
def launch(request):

    valid_school = False
    valid_department = False
    user_in_whitelist = False
    user_can_access = False
    #valid_school_code = None
    firstname = None
    lastname = None
    email = None
    role = None
    division = None
    client_ip = getclientip(request)

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 5 minutes (18000 seconds)
    
    currenttime = time.time()
    timestamp = datetime.datetime.fromtimestamp(currenttime).strftime('%Y-%m-%dT%H:%M:%S')
    exp_ts = time.time() + 18000
    exp_date = datetime.datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%dT%H:%M:%S')
 
    huid = request.user.username
    persondataobj = IcommonsApi(huid)
    resp = persondataobj.getpersondata()

    if resp.status_code == 200:
        data = resp.json()
        userdict = builduserdict(data)
        firstname = userdict['firstname']
        lastname = userdict['lastname']
        email = userdict['email']
        role = userdict['role']
        division = userdict['division']

    else:
        loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
        logger.error(loggmsg)
        return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'response code '+str(resp.status_code)})

    user_in_whitelist = isuserinwhitelist(huid)
 
    if valid_department or valid_school or user_in_whitelist:
        user_can_access = True

    if user_can_access:
        #Check to see if the user has accepted the terms of service    
        agreementid = settings.QUALTRICS_LINK['AGREEMENT_ID']
        acceptance_resp = persondataobj.getuseracceptance(agreementid)
        
        if acceptance_resp.status_code == 200:
            acceptance_json = acceptance_resp.json()
            if 'agreements' in acceptance_json:
                lenth = len(acceptance_json['agreements'])
                if lenth > 0:
                    acceptance_text = acceptance_json['agreements'][0]['text']
                    return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement' : acceptance_text})
            else:
                loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
                logger.error(loggmsg)
                return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'error retrieving acceptance_resp'})
        else:
            loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
            logger.error(loggmsg)
            return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'Agreement service call returned '+acceptance_resp.status_code})

        enc_id = getencryptedhuid(huid)
        keyvaluepairs = "id="+enc_id+"&timestamp="+timestamp+"&expiration="+exp_date+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
        qualtricslink = getqualtricsurl(keyvaluepairs) #'https://harvard.qualtrics.com/ControlPanel/?ssotoken='+encodedtoken
        logline = "{}\t{}\t{}\t{}".format(timestamp, client_ip, role, division)
        logger.info(logline)

        #the redirect line below will be how the application works if everything is good for the user. 
        return redirect(qualtricslink)

    else:
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})


@login_required
@require_http_methods(['GET'])
def internal(request):

    valid_school = False
    valid_department = False
    user_in_whitelist = False
    user_can_access = False
    #valid_school_code = None
    firstname = None
    lastname = None
    email = None
    role = None
    division = None
    client_ip = getclientip(request)


    # get the current date in the correct format i.e. '2008-07-16T15:42:51'

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')

    
    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 15 minutes (900 seconds)
    
    exp_ts = time.time() + 18000
    exp_date = datetime.datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%dT%H:%M:%S')

    
    # get the users id from the session, then encrypt it using the hashlib.md5 method. 
    # Example of my huid from the qualtrics site: 3190b96f2c08b147f504034dfc051a8d#harvard
    # The id matches minus the #harvard at the end.
    
    if 'huid' in request.GET: # If the form has been submitted...
        # ContactForm was defined in the the previous section
        form = SpoofForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            huid = request.GET['huid']
            if huid == '':
                huid = request.user.username
    else:
        form = SpoofForm() # An unbound form
        huid = request.user.username

    persondataobj = IcommonsApi(huid)
    resp = persondataobj.getpersondata()

    if resp.status_code == 200:
        data = resp.json()
        userdict = builduserdict(data)
        firstname = userdict['firstname']
        lastname = userdict['lastname']
        email = userdict['email']
        role = userdict['role']
        division = userdict['division']

    else:
        loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
        logger.error(loggmsg)
        return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'response code '+str(resp.status_code)})

    user_in_whitelist = isuserinwhitelist(huid)
 
    if valid_department or valid_school or user_in_whitelist:
        user_can_access = True

    if user_can_access:
        #Check to see if the user has accepted the terms of service    
        agreementid = settings.QUALTRICS_LINK['AGREEMENT_ID']
        acceptance_resp = persondataobj.getuseracceptance(agreementid)
        
        if acceptance_resp.status_code == 200:
            acceptance_json = acceptance_resp.json()
            if 'agreements' in acceptance_json:
                lenth = len(acceptance_json['agreements'])
                if lenth > 0:
                    acceptance_text = acceptance_json['agreements'][0]['text']
                    return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement' : acceptance_text})
            else:
                loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
                logger.error(loggmsg)
                return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'error retrieving acceptance_resp'})
        else:
            loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
            logger.error(loggmsg)
            return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'Agreement service call returned '+acceptance_resp.status_code})

        
        enc_id = getencryptedhuid(huid)

        keyvaluedict = {
            'id' : enc_id,
            'timestamp' : timestamp,
            'expiration' : exp_date,
            'firstname' : firstname,
            'lastname' : lastname,
            'email' : email,
            'role' : role,
            'division' : division,
        }

        logline = "{}\t{}\t{}\t{}".format(timestamp, client_ip, role, division)
        logger.info(logline)

        keyvaluepairs = "id="+enc_id+"&timestamp="+timestamp+"&expiration="+exp_date+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
        
        ssotestlink = getssotesturl(keyvaluepairs)
        qualtricslink = getqualtricsurl(keyvaluepairs) #'https://harvard.qualtrics.com/ControlPanel/?ssotoken='+encodedtoken

        #the redirect line below will be how the application works if everything is good for the user. 
        if settings.DEBUG:
            logger.info('IN DEBUG MODE')
            return render(request, 'qualtrics_link/main.html', {'request': request, 'qualtricslink' : qualtricslink, 'ssotestlink': ssotestlink, 'huid' : huid, 'user_in_whitelist' : user_in_whitelist, 'keyValueDict' :  keyvaluedict, 'person' : userdict, 'form' : form})
        else:
            return redirect(qualtricslink)
    else:
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request, 'person' : person, 'division' : division})


@login_required
@require_http_methods(['GET'])
def user_accept_terms(request):
    
    # this is handy for debugging the post request
    #import httplib
    #httplib.HTTPConnection.debuglevel = 1

    huid = request.user.username
    persondataobj = IcommonsApi(huid)
    ipaddress = getclientip(request)
    params = {'agreementId' : '260', 'ipAddress' : ipaddress,}
    resp = persondataobj.create_acceptance(params)
    #data = json.dumps(params)
    #useracceptanceurl = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'policy_agreement/create_acceptance/'+huid
    #sslsession = requests.Session()
    #sslsession.mount('https://', MyAdapter())
    #headers = {'content-type': 'application/x-www-form-urlencoded'}
    #resp = sslsession.post(useracceptanceurl, verify=False, \
    #    data=params, headers=headers, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
    
    if resp.status_code == 200:
        logger.info(resp.text)
        return redirect('ql:launch')
    else:
        return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'no people were found'})
    
    return render(request, 'qualtrics_link/main.html', {'request': request})

@login_required
@require_http_methods(['GET'])
def user_decline_terms(request):

    return render(request, 'qualtrics_link/main.html', {'request': request})


@login_required
@require_http_methods(['GET'])
def get_org_info(request):

    apiurl = settings.QUALTRICS_LINK['QUALTRICS_API_URL']
    enddate = date.today().strftime("%Y-%m-%d")

    query = {
        'Request' : 'getResponseCountsByOrganization',
        'User' : settings.QUALTRICS_LINK['QUALTRICS_API_USER'],
        'Token' : settings.QUALTRICS_LINK['QUALTRICS_API_TOKEN'],
        'StartDate' : '2010-01-01',
        'EndDate' : enddate,
        'Format' : 'JSON',
        'Version' : '2.0',
    }

    params = urllib.urlencode(query)
    f = urllib.urlopen(apiurl, params)
    responsecounts = '{ "getResponseCountsByOrganization" : '+f.read()+ '}'

    query2 = {
        'Request' : 'getOrgActivity',
        'User' : settings.QUALTRICS_LINK['QUALTRICS_API_USER'],
        'Token' : settings.QUALTRICS_LINK['QUALTRICS_API_TOKEN'],
        'Format' : 'JSON',
        'Version' : '2.0',
        'Organization' : 'harvard', 
    }

    params = urllib.urlencode(query2)
    f = urllib.urlopen(apiurl, params)
    orgactivity = '{ "getOrgActivity" : '+f.read()+ '}'

    result = '{ "org_info" : ['+responsecounts+ ','+orgactivity+' ]}'

    return HttpResponse(result, content_type="application/json")

@login_required
@require_http_methods(['GET'])
def main(request):

	logger.debug('Now in main')
	return render(request, 'qualtrics_link/main.html', {'request': request })





    