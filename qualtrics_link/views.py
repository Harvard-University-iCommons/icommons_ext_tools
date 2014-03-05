

from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
#from time import time
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from icommons_common.monitor.views import BaseMonitorResponseView
from icommons_common.models import QualtricsAccessList
from django.http import HttpResponse
import time
import datetime
from datetime import date
import urllib
from qualtrics_link.icommonsapi import IcommonsApi
from qualtrics_link.util import *
from qualtrics_link.forms import SpoofForm

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

    validschool = False
    validdepartment = False
    userinwhitelist = False
    usercanaccess = False
    firstname = None
    lastname = None
    email = None
    role = None
    division = None
    clientip = getclientip(request)

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 1 minutes (60 seconds)
    currenttime = time.time()
    currentdate = datetime.datetime.utcfromtimestamp(currenttime).strftime('%Y-%m-%dT%H:%M:%S')

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 5 minutes (300 seconds)
    expirationdate = datetime.datetime.utcfromtimestamp(currenttime + 300).strftime('%Y-%m-%dT%H:%M:%S')

    huid = request.user.username
    persondataobj = IcommonsApi()
    resp = persondataobj.getpersondata(huid)

    if resp.status_code == 200:
        data = resp.json()
        userdict = builduserdict(data)
        firstname = userdict['firstname']
        lastname = userdict['lastname']
        email = userdict['email']
        role = userdict['role']
        division = userdict['division']
        if 'validschool' in userdict:
            validschool = userdict['validschool']
        if 'validdept' in userdict:    
            validdepartment = userdict['validdept']

    else:
        loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
        logger.error(loggmsg)
        return render(request, 'qualtrics_link/error.html', {'request': request})

    userinwhitelist = isuserinwhitelist(huid)
 
    # check if the user can use qualtrics or not
    # the value of usercanaccess is set to False by default
    # if any of the checks here pass we set usercanaccess to True
    if validdepartment or validschool or userinwhitelist:
        usercanaccess = True

    if usercanaccess:
        #Check to see if the user has accepted the terms of service    
        agreementid = settings.QUALTRICS_LINK['AGREEMENT_ID']
        acceptance_resp = persondataobj.getuseracceptance(agreementid, huid)
        
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
                return render(request, 'qualtrics_link/error.html', {'request': request})
        else:
            loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
            logger.error(loggmsg)
            return render(request, 'qualtrics_link/error.html', {'request': request})

        enc_id = getencryptedhuid(huid)
        keyvaluepairs = "id="+enc_id+"&timestamp="+currentdate+"&expiration="+expirationdate+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
        qualtricslink = getqualtricsurl(keyvaluepairs) #'https://harvard.qualtrics.com/ControlPanel/?ssotoken='+encodedtoken
        logline = "{}\t{}\t{}\t{}".format(time.time(), clientip, role, division)
        logger.info(logline)

        #the redirect line below will be how the application works if everything is good for the user. 
        return redirect(qualtricslink)

    else:
        logline = "notauthorized\t{}\t{}\t{}\t{}".format(time.time(), clientip, role, division)
        logger.info(logline)
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})


@login_required
@require_http_methods(['GET'])
def internal(request):

    validschool = False
    validdepartment = False
    userinwhitelist = False
    usercanaccess = False
    firstname = None
    lastname = None
    email = None
    role = None
    division = None
    clientip = getclientip(request)

    # get the current date in the correct format i.e. '2008-07-16T15:42:51'
    currenttime = time.time()
    currentdate = datetime.datetime.utcfromtimestamp(currenttime).strftime('%Y-%m-%dT%H:%M:%S')

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 10 minutes (600 seconds)
    expirationdate = datetime.datetime.utcfromtimestamp(currenttime + 600).strftime('%Y-%m-%dT%H:%M:%S')

    # get the users id from the session, then encrypt it using the hashlib.md5 method. 
    # Example of my huid from the qualtrics site: 3190b96f2c08b147f504034dfc051a8d#harvard
    # The id matches minus the #harvard at the end.
    
    if 'huid' in request.GET: # If the form has been submitted...
        # ContactForm was defined in the the previous section
        spoofform = SpoofForm(request.GET) # A form bound to the POST data
        if spoofform.is_valid(): # All validation rules pass
            huid = request.GET['huid']
            if huid == '':
                huid = request.user.username
    else:
        spoofform = SpoofForm() # An unbound form
        huid = request.user.username

    persondataobj = IcommonsApi()
    person = persondataobj.getpersondata(huid)

    if person.status_code == 200:
        data = person.json()
        user = data['people'][0]
        userdict = builduserdict(data)
        firstname = userdict['firstname']
        lastname = userdict['lastname']
        email = userdict['email']
        role = userdict['role']
        division = userdict['division']
        if 'validschool' in userdict:
            validschool = userdict['validschool']
        if 'validdept' in userdict:    
            validdepartment = userdict['validdept']
        userdict['currenttime'] = currentdate
        userdict['expirationtime'] = expirationdate

    else:
        loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(person.status_code))
        logger.error(loggmsg)
        return render(request, 'qualtrics_link/error.html', {'request': request})

    userinwhitelist = isuserinwhitelist(huid)
 
    # check if the user can use qualtrics or not
    # the value of usercanaccess is set to False by default
    # if any of the checks here pass we set usercanaccess to True
    if validdepartment or validschool or userinwhitelist:
        usercanaccess = True
    
    if usercanaccess:
        # If they are allowed to use Qualtrics, check to see if the user has accepted the terms of service    
        agreementid = settings.QUALTRICS_LINK['AGREEMENT_ID']
        acceptance_resp = persondataobj.getuseracceptance(agreementid, huid)
        
        if acceptance_resp.status_code == 200:
            acceptance_json = acceptance_resp.json()
            if 'agreements' in acceptance_json:
                lenth = len(acceptance_json['agreements'])
                if lenth > 0:
                    acceptance_text = acceptance_json['agreements'][0]['text']
                    return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement' : acceptance_text})
            else:
                loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(person.status_code))
                logger.error(loggmsg)
                return render(request, 'qualtrics_link/error.html', {'request': request})
        else:
            loggmsg = 'huid: {}, api call returned response code {}'.format(huid, str(person.status_code))
            logger.error(loggmsg)
            return render(request, 'qualtrics_link/error.html', {'request': request})

        
        enc_id = getencryptedhuid(huid)
        logline = "{}\t{}\t{}\t{}".format(time.time(), clientip, role, division)
        logger.info(logline)
        keyvaluepairs = "id="+enc_id+"&timestamp="+currentdate+"&expiration="+expirationdate+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
        ssotestlink = getssotesturl(keyvaluepairs)
        qualtricslink = getqualtricsurl(keyvaluepairs) #'https://harvard.qualtrics.com/ControlPanel/?ssotoken='+encodedtoken

        return render(request, 'qualtrics_link/main.html', {'request': request, 'qualtricslink' : qualtricslink, 'ssotestlink': ssotestlink, 'huid' : huid, 'user_in_whitelist' : userinwhitelist, 'keyValueDict' :  userdict, 'person' : user, 'form' : spoofform})
        
    else:
        logline = "notauthorized\t{}\t{}\t{}\t{}".format(time.time(), clientip, role, division)
        logger.info(logline)
        return render(request, 'qualtrics_link/notauthinternal.html', {'request': request, 'person' : user, 'division' : division})


@login_required
@require_http_methods(['GET'])
def user_accept_terms(request):
    
    # this is handy for debugging the post request
    #import httplib
    #httplib.HTTPConnection.debuglevel = 1

    huid = request.user.username
    persondataobj = IcommonsApi()
    ipaddress = getclientip(request)
    params = {'agreementId' : '260', 'ipAddress' : ipaddress,}
    resp = persondataobj.create_acceptance(params, huid)
    
    if resp.status_code == 200:
        logger.info(resp.text)
        return redirect('ql:launch')
    else:
        return render(request, 'qualtrics_link/error.html', {'request': request})
    
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
    apiresponse = urllib.urlopen(apiurl, params)
    responsecounts = '{ "getResponseCountsByOrganization" : '+apiresponse.read()+ '}'
    apiresponse = None

    query2 = {
        'Request' : 'getOrgActivity',
        'User' : settings.QUALTRICS_LINK['QUALTRICS_API_USER'],
        'Token' : settings.QUALTRICS_LINK['QUALTRICS_API_TOKEN'],
        'Format' : 'JSON',
        'Version' : '2.0',
        'Organization' : 'harvard', 
    }

    params = urllib.urlencode(query2)
    apiresponse = urllib.urlopen(apiurl, params)
    orgactivity = '{ "getOrgActivity" : '+apiresponse.read()+ '}'
    result = '{ "org_info" : ['+responsecounts+ ','+orgactivity+' ]}'
    return HttpResponse(result, content_type="application/json")





    