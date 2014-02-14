

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


#BLOCK_SIZE=16
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]

"""
We make the black list a set to make it very easy to test if an item is a member.
We can do the following [ 'item' in blacklist ] which will return true or false.
"""
blackList = set(['HBS','HMS','HSDM'])

AREA_LOOKUP = {
    'SUM'  : 'EXT',
    'EXT'  : 'EXT',
    'DCE'  : 'EXT',
    'ECS'  : 'EXT',
    'FAS'  : 'FAS',
    'EAS'  : 'FAS', 
    'COL'  : 'FAS',
    'FGS'  : 'FAS',
    'GSD'  : 'GSD',
    'DES'  : 'GSD',
    'EDU'  : 'GSE',
    'GSE'  : 'GSE',
    'HDS'  : 'HDS',
    'DIV'  : 'HDS',
    'HKS'  : 'HKS',
    'KSG'  : 'HKS',
    'HLS'  : 'HLS',
    'LAW'  : 'HLS',
    'HSPH' : 'HSPH',
    'SPH'  : 'HSPH',
    'UIS'  : 'HUIT',
    'HUIT' : 'HUIT',
    'HBS'  : 'HBS',
    'HSDM' : 'HSDM',
    'HMS'  : 'HMS',
}

def lookupunit(unit):
    if unit in AREA_LOOKUP:
        return AREA_LOOKUP[unit]
    else:
        return 'Other'

def getValidSchool(schools):
    for schoolcode in schools:
        logger.debug('schoolcode='+schoolcode)
        school = lookupunit(schoolcode)
        if  school not in blackList:
            logger.debug('valid_school='+school)
            return school
        else:
            logger.debug('school in blacklist: '+school)
    return None

def isDeptValid(dept):
    if dept.lower() == 'not available':
        return False
    division = lookupunit(dept)
    if  division in blackList:
        return False
    return True

def isuserinwhitelist(huid):
    print huid
    return True


@require_http_methods(['GET'])
def index(request):
    return render(request, 'qualtrics_link/index.html')

@login_required
@require_http_methods(['GET'])
def launch(request):

    valid_school = False
    valid_department = False
    user_in_whitelist = False
    #valid_school_code = None
    firstname = None
    lastname = None
    email = None
    role = 'generic'
    division = 'Other'
    
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
    #huid = request.user.username
    #huid = '90699342' # id with mutiple schools
    huid = '70855038'
    """
    Check to see if the user has accepted the terms of service
    """
    agreementid = '260'
    acceptance_url = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'policy_agreement/acceptance/'+agreementid+'/'+huid+'.json'
    acceptance_session = requests.Session()
    acceptance_session.mount('https://', MyAdapter())
    acceptance_resp = acceptance_session.get( acceptance_url , verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
    
    if acceptance_resp.status_code == 200:
        acceptance_json = acceptance_resp.json()
        if 'agreements' in acceptance_json:
            lenth = len(acceptance_json['agreements'])
            if lenth > 0:
                acceptance_text = acceptance_json['agreements'][0]['text']
                return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement' : acceptance_text })
        else:
             return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'error retrieving acceptance_resp' })
    else:
        return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'Agreement service call returned '+acceptance_resp.status_code })


    peopleurl = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'people/by_id/'+huid+'.json'
    s = requests.Session()
    s.mount('https://', MyAdapter())
    resp = s.get(peopleurl , verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
    
    if resp.status_code == 200:
        data = resp.json()
        if 'people' in data:
            person = data['people'][0]

            """
            We should return an error if firstname, lastname, or email is empty
            """

            if 'firstName' in person:
                firstname = person['firstName']
            else:
                firstname = None

            if 'lastName' in person:
                lastname = person['lastName']
            else:
                lastname = None

            if 'email' in person:
                email = person['email']
            else:
                email = None

            """
            School Affiliations check
            """
            if 'schoolAffiliations' in person:
                schoolaffiliations = person['schoolAffiliations']
                valid_school_code = getValidSchool(schoolaffiliations)
                if valid_school_code:
                    valid_school = True
                    role = 'student'
                    division = valid_school_code
                    logger.debug('valid_school='+str(valid_school_code))
                else:
                    logger.debug('no schoolaffiliations found')
            else:
                schoolaffiliations = None


            """
            Person Affiliations check
            
            if 'personAffiliation' in person:
                personaffiliation = person['personAffiliation']
                if personaffiliation.lower() != 'not available':
                    role = personaffiliation
            else:
                personaffiliation = None
            """

            """
            Department Affiliations check
            """
            if 'departmentAffiliation' in person:
                departmentaffiliation = person['departmentAffiliation']
                valid_department = isDeptValid(departmentaffiliation)
                if valid_department:
                    valid_department = True
                    role = 'employee'
                    division = departmentaffiliation
                    valid_department_code = departmentaffiliation
                    logger.debug('valid_department='+str(departmentaffiliation))
            else:
                departmentaffiliation = None

        else:
            return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'no people were found' })
    else:
        return render(request, 'qualtrics_link/error.html', {'request': request, 'msg' : 'response code '+resp.status_code })

 
    if valid_department or valid_school or isuserinwhitelist(huid):
        m = hashlib.md5()
        m.update(huid)
        enc_id = m.hexdigest()

        keyvaluedict = {
            'id' : enc_id,
            'timestamp' : date,
            'expiration' : exp_date,
            'firstname' : firstname,
            'lastname' : lastname,
            'email' : email,
            'role' : role,
            'division' : division,
        }

        keyValuePairs = "id="+enc_id+"&timestamp="+date+"&expiration="+exp_date+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
        key = settings.QUALTRICS_LINK['QUALTRICS_APP_KEY']
        secret = bytes(key)
        data = bytes(keyValuePairs)
        encoded = base64.b64encode( hmac.new( secret, data, hashlib.sha256 ).digest() )
        token = keyValuePairs + '&mac=' + encoded; 
        raw = pad(token)
        cipher = AES.new( key, AES.MODE_ECB)
        encodedToken =  base64.b64encode( cipher.encrypt( raw ) ) 
        link = 'https://new.qualtrics.com/ControlPanel/ssoTest.php?key='+key+'&mac=sha256&ssotoken='+encodedToken

        """
        the redirect line below will be how the application works if everything is good for the user. 
        """
        #return redirect(link)

        return render(request, 'qualtrics_link/main.html', {'request': request, 'link' : link, 'huid' : huid, 'keyValueDict' :  keyvaluedict })

@login_required
@require_http_methods(['POST'])
def user_accept_terms(request):

    return render(request, 'qualtrics_link/main.html', {'request': request})

@login_required
@require_http_methods(['POST'])
def user_decline_terms(request):

    return render(request, 'qualtrics_link/main.html', {'request': request })


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





    