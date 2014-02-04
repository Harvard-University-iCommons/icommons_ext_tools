

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

#from util import util

logger = logging.getLogger(__name__)


'''
We need to subclass the HttpAdater class to allow connections
to SSL version 1. 
'''
class MyAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


BLOCK_SIZE=16
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]


@require_http_methods(['GET'])
def index(request):
    logger.info("request to index.")
    return render(request, 'qualtrics_link/index.html')

@login_required
@require_http_methods(['GET'])
def launch(request):

    
    logger.debug("redirect user to the first page")
    
    """
    get the current date in the correct format i.e. '2008-07-16T15:42:51'
    """
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%dT%H:%M:%S')

    """
    get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    In this case we take the current time and add 15 minutes (900 seconds)
    """
    exp_ts = time.time() + 9999999
    exp_date = datetime.datetime.fromtimestamp(exp_ts).strftime('%Y-%m-%dT%H:%M:%S')

    """
    get the users id from the session, then encrypt it using the hashlib.md5 method. 
    Example of my huid from the qualtrics site: 3190b96f2c08b147f504034dfc051a8d#harvard
    The id matches minus the #harvard at the end.
    """
    huid = request.user.username
    m = hashlib.md5()
    m.update(huid)
    enc_id = m.hexdigest()

    peopleurl = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'people/by_id/'+huid+'.json'
    s = requests.Session()
    s.mount('https://', MyAdapter())
    resp = s.get(peopleurl , verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
    if resp.status_code == 200:
        data = resp.json()
        if 'people' in data:
            person = data['people'][0]
            if 'firstName' in person:
                firstname = person['firstName']
            else:
                firstname = ''
            if 'lastName' in person:
                lastname = person['lastName']
            else:
                lastname = ''
            if 'email' in person:
                email = person['email']
            else:
                email = ''
            if 'schoolAffiliations' in person:
                schoolaffiliations = person['schoolAffiliations']
            else:
                schoolaffiliations = ''
            if 'personAffiliation' in person:
                personaffiliation = person['personAffiliation']
            else:
                personaffiliation = ''
            if 'departmentAffiliation' in person:
                departmentaffiliation = person['departmentAffiliation']
            else:
                departmentaffiliation = ''
        else:
            return render(request, 'qualtrics_link/error.html', {'request': request, 'error' : 'no people were found' })
    else:
        return render(request, 'qualtrics_link/error.html', {'request': request, 'error' : 'response code '+resp.status_code })

    role = ''
    division = ''

    keyValuePairs = "id="+enc_id+"&timestamp="+date+"&expiration="+exp_date+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
    key = settings.QUALTRICS_LINK['QUALTRICS_APP_KEY']
    secret = bytes(key)
    data = bytes(keyValuePairs)
    encoded = base64.b64encode( hmac.new( secret, data ).digest() )
    token = keyValuePairs + '&mac=' + encoded; 
    raw = pad(token)
    cipher = AES.new( key, AES.MODE_ECB)
    encodedToken =  base64.b64encode( cipher.encrypt( raw ) ) 
    link = 'https://new.qualtrics.com/ControlPanel/ssoTest.php?key='+key+'&mac=md5&ssotoken='+encodedToken

    return redirect(link)

@login_required
@require_http_methods(['GET'])
def org_info(request):

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





    