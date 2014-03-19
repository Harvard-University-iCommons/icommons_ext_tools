

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
import qualtrics_link.util
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
    clientip = qualtrics_link.util.getclientip(request)

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 1 minutes (60 seconds)
    currenttime = time.time()
    currentdate = datetime.datetime.utcfromtimestamp(currenttime).strftime('%Y-%m-%dT%H:%M:%S')

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 5 minutes (300 seconds)
    expirationdate = datetime.datetime.utcfromtimestamp(currenttime + 300).strftime('%Y-%m-%dT%H:%M:%S')

    huid = request.user.username

    # make sure this is an HUID
    if not huid.isdigit():
        logline = "xidnotauthorized\t{}\t{}".format(currentdate, clientip)
        logger.info(logline)
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})
    
    persondataobj = IcommonsApi()
    resp = persondataobj.people_by_id(huid)

    if resp.status_code == 200:
        data = resp.json()
        userdict = qualtrics_link.util.builduserdict(data)
        firstname = userdict.get('firstname')
        lastname = userdict.get('lastname')
        email = userdict.get('email')
        role = userdict.get('role')
        division = userdict.get('division')
        if 'validschool' in userdict:
            validschool = userdict.get('validschool')
        if 'validdept' in userdict:    
            validdepartment = userdict.get('validdept')

    else:
        logmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
        logger.error(logmsg)
        return render(request, 'qualtrics_link/error.html', {'request': request})

    userinwhitelist = qualtrics_link.util.isuserinwhitelist(huid)
 
    # check if the user can use qualtrics or not
    # the value of usercanaccess is set to False by default
    # if any of the checks here pass we set usercanaccess to True
    if validdepartment or validschool or userinwhitelist:
        usercanaccess = True

    if usercanaccess:
        #Check to see if the user has accepted the terms of service    
        agreementid = settings.QUALTRICS_LINK.get('AGREEMENT_ID', '260')
        acceptance_resp = persondataobj.tos_get_acceptance(agreementid, huid)
        
        if acceptance_resp.status_code == 200:
            acceptance_json = acceptance_resp.json()
            if 'agreements' in acceptance_json:
                lenth = len(acceptance_json['agreements'])
                if lenth > 0:
                    acceptance_text = acceptance_json['agreements'][0]['text']
                    return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement' : acceptance_text})
            else:
                logmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
                logger.error(logmsg)
                return render(request, 'qualtrics_link/error.html', {'request': request})
        else:
            logmsg = 'huid: {}, api call returned response code {}'.format(huid, str(resp.status_code))
            logger.error(logmsg)
            return render(request, 'qualtrics_link/error.html', {'request': request})

        enc_id = qualtrics_link.util.getencryptedhuid(huid)
        keyvaluepairs = "id="+enc_id+"&timestamp="+currentdate+"&expiration="+expirationdate+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
        qualtricslink = qualtrics_link.util.getqualtricsurl(keyvaluepairs) 
        logline = "{}\t{}\t{}\t{}".format(currentdate, clientip, role, division)
        logger.info(logline)

        #the redirect line below will be how the application works if everything is good for the user. 
        return redirect(qualtricslink)

    else:
        logline = "notauthorized\t{}\t{}\t{}\t{}".format(currentdate, clientip, role, division)
        logger.info(logline)
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})


@login_required
@group_membership_restriction(settings.QUALTRICS_LINK.get('QUALTRICS_AUTH_GROUP'))
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
    clientip = qualtrics_link.util.getclientip(request)

    # get the current date in the correct format i.e. '2008-07-16T15:42:51'
    currenttime = time.time()
    currentdate = datetime.datetime.utcfromtimestamp(currenttime).strftime('%Y-%m-%dT%H:%M:%S')

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 10 minutes (600 seconds)
    expirationdate = datetime.datetime.utcfromtimestamp(currenttime + 600).strftime('%Y-%m-%dT%H:%M:%S')

 
    # Form to allow admins to spoof other users
    if 'huid' in request.GET: # If the form has been submitted...
        # ContactForm was defined in the the previous section
        spoofform = SpoofForm(request.GET) # A form bound to the POST data
        if spoofform.is_valid(): # All validation rules pass
            huid = request.GET['huid']
            huid = huid.strip()
            logger.info('USER: '+str(request.user.username)+ ' Spoofing: ' +huid)
            if huid == '':
                if 'spoofid' in request.session:
                    del request.session['spoofid']
                huid = request.user.username
                
    elif 'spoofid' in request.session:
        # we got here becuase the user accepted the tos and we needed a way to stay the spoofed user
        huid = request.session.get('spoofid')
        huid = huid.strip()
        
        logger.info('USER: '+str(request.user.username)+ ' Spoofing: ' +str(request.session.get('spoofid', 'None')))
        
        spoofform = SpoofForm({'huid' : huid.strip()})
    else:
        spoofform = SpoofForm() # An unbound form
        huid = request.user.username
        huid = huid.strip()


    if not huid.isdigit():
        logline = "xidnotauthorized\t{}\t{}".format(currentdate, clientip)
        logger.info(logline)
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})



    # initialize the icommons api module
    persondataobj = IcommonsApi()
    person = persondataobj.people_by_id(huid)

    if person.status_code == 200:
        data = person.json()
        user = data['people'][0]
        userdict = qualtrics_link.util.builduserdict(data)
        firstname = userdict.get('firstname')
        lastname = userdict.get('lastname')
        email = userdict.get('email')
        role = userdict.get('role')
        division = userdict.get('division')
        if 'validschool' in userdict:
            validschool = userdict.get('validschool')
        if 'validdept' in userdict:    
            validdepartment = userdict.get('validdept')
        userdict['currenttime'] = currentdate
        userdict['expirationtime'] = expirationdate

    else:
        logmsg = 'huid: {}, api call returned response code {}'.format(huid, str(person.status_code))
        logger.error(logmsg)
        return render(request, 'qualtrics_link/error.html', {'request': request})

    userinwhitelist = qualtrics_link.util.isuserinwhitelist(huid)
 
    # check if the user can use qualtrics or not
    # the value of usercanaccess is set to False by default
    # if any of the checks here pass we set usercanaccess to True
    if validdepartment or validschool or userinwhitelist:
        usercanaccess = True
    
    if usercanaccess:
        # If they are allowed to use Qualtrics, check to see if the user has accepted the terms of service    
        agreementid = settings.QUALTRICS_LINK.get('AGREEMENT_ID')
        acceptance_resp = persondataobj.tos_get_acceptance(agreementid, huid)
        
        if acceptance_resp.status_code == 200:
            acceptance_json = acceptance_resp.json()
            if 'agreements' in acceptance_json:
                lenth = len(acceptance_json['agreements'])
                if lenth > 0:
                    acceptance_text = acceptance_json['agreements'][0]['text']
                    request.session['spoofid'] = huid
                    return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement' : acceptance_text})
            else:
                logmsg = 'huid: {}, api call returned response code {}'.format(huid, str(person.status_code))
                logger.error(logmsg)
                return render(request, 'qualtrics_link/error.html', {'request': request})
        else:
            logmsg = 'huid: {}, api call returned response code {}'.format(huid, str(person.status_code))
            logger.error(logmsg)
            return render(request, 'qualtrics_link/error.html', {'request': request})

        enc_id = qualtrics_link.util.getencryptedhuid(huid)
        logline = "{}\t{}\t{}\t{}".format(currentdate, clientip, role, division)
        logger.info(logline)
        keyvaluepairs = "id="+enc_id+"&timestamp="+currentdate+"&expiration="+expirationdate+"&firstname="+firstname+"&lastname="+lastname+"&email="+email+"&UserType="+role+"&Division="+division
        ssotestlink = qualtrics_link.util.getssotesturl(keyvaluepairs)
        qualtricslink = qualtrics_link.util.getqualtricsurl(keyvaluepairs) #'https://harvard.qualtrics.com/ControlPanel/?ssotoken='+encodedtoken
        return render(request, 'qualtrics_link/main.html', {'request': request, 'qualtricslink' : qualtricslink, 'ssotestlink': ssotestlink, 'huid' : huid, 'user_in_whitelist' : userinwhitelist, 'keyValueDict' :  userdict, 'person' : user, 'form' : spoofform})
        
    else:
        logline = "notauthorized\t{}\t{}\t{}\t{}".format(currentdate, clientip, role, division)
        logger.info(logline)
        return render(request, 'qualtrics_link/notauthinternal.html', {'request': request, 'person' : user, 'division' : division})

@login_required
@require_http_methods(['GET'])
def user_accept_terms(request):
    
    # this is handy for debugging the post request
    #import httplib
    #httplib.HTTPConnection.debuglevel = 1

    huid = request.session.get('spoofid', False)
    if not huid:
        huid = request.user.username

    persondataobj = IcommonsApi()
    ipaddress = qualtrics_link.util.getclientip(request)
    params = {'agreementId' : '260', 'ipAddress' : ipaddress,}
    resp = persondataobj.tos_create_acceptance(params, huid)
    
    if resp.status_code == 200:
        logger.info(resp.text)
        return redirect(settings.QUALTRICS_LINK.get('USER_ACCEPTED_TERMS_URL', 'ql:launch'))
    else:
        return render(request, 'qualtrics_link/error.html', {'request': request})
    
    return render(request, 'qualtrics_link/main.html', {'request': request})

@login_required
@require_http_methods(['GET'])
def user_decline_terms(request):

    return redirect(settings.QUALTRICS_LINK.get('USER_DECLINED_TERMS_URL', 'http://surveytools.harvard.edu'))


@require_http_methods(['GET'])
def get_org_info(request):

    apiurl = settings.QUALTRICS_LINK.get('QUALTRICS_API_URL')
    enddate = date.today().strftime("%Y-%m-%d")

    query = {
        'Request' : 'getResponseCountsByOrganization',
        'User' : settings.QUALTRICS_LINK.get('QUALTRICS_API_USER'),
        'Token' : settings.QUALTRICS_LINK.get('QUALTRICS_API_TOKEN'),
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
        'User' : settings.QUALTRICS_LINK.get('QUALTRICS_API_USER'),
        'Token' : settings.QUALTRICS_LINK.get('QUALTRICS_API_TOKEN'),
        'Format' : 'JSON',
        'Version' : '2.0',
        'Organization' : 'harvard', 
    }

    params = urllib.urlencode(query2)
    apiresponse = urllib.urlopen(apiurl, params)
    orgactivity = '{ "getOrgActivity" : '+apiresponse.read()+ '}'
    result = '{ "org_info" : ['+responsecounts+ ','+orgactivity+' ]}'
    return HttpResponse(result, content_type="application/json")





    