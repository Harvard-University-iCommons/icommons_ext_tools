from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from icommons_common.monitor.views import BaseMonitorResponseView
from icommons_common.icommonsapi import IcommonsApi
from icommons_common.auth.decorators import group_membership_restriction
from django.http import HttpResponse
from datetime import date
import time
import datetime
import urllib
from qualtrics_link.forms import SpoofForm
import qualtrics_link.util as util
from django.conf import settings

logger = logging.getLogger(__name__)


class MonitorResponseView(BaseMonitorResponseView):
    def healthy(self):
        return True

# BLOCK_SIZE=16
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s: s[0:-ord(s[-1])]


@require_http_methods(['GET'])
def index(request):
    return render(request, 'qualtrics_link/index.html')


@login_required
@require_http_methods(['GET'])
def launch(request):
    icommons_api = IcommonsApi()
    user_can_access = False
    client_ip = util.get_client_ip(request)

    # Get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 1 minutes (60 seconds)
    current_time = time.time()
    current_date = datetime.datetime.utcfromtimestamp(current_time).strftime('%Y-%m-%dT%H:%M:%S')

    # Get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 5 minutes (300 seconds)
    expiration_date = datetime.datetime.utcfromtimestamp(current_time + 300).strftime('%Y-%m-%dT%H:%M:%S')

    huid = request.user.username
    user_in_whitelist = util.is_user_in_whitelist(huid)

    # make sure this is an HUID
    if not huid.isdigit() and not user_in_whitelist:
        logger.info("xidnotauthorized\t{}\t{}".format(current_date, client_ip))
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})
    
    # The PersonDetails object extends the Person model with additional attributes
    person_details = util.get_person_details(huid, request)

    # Check if the user can use qualtrics or not
    # the value of user_can_access is set to False by default
    # if any of the checks here pass we set user_can_access to True
    if person_details.valid_department or person_details.valid_school or user_in_whitelist:
        user_can_access = True

    if user_can_access:
        # Check to see if the user has accepted the terms of service
        agreement_id = settings.QUALTRICS_LINK.get('AGREEMENT_ID', '260')
        acceptance_resp = icommons_api.tos_get_acceptance(agreement_id, huid)
        
        if acceptance_resp.status_code == 200:
            acceptance_json = acceptance_resp.json()
            if 'agreements' in acceptance_json:
                length = len(acceptance_json['agreements'])
                if length > 0:
                    acceptance_text = acceptance_json['agreements'][0]['text']
                    return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement': acceptance_text})
            else:
                logger.error('huid: {}, api call returned response code {}'.format(huid, str(acceptance_resp.status_code)))
                return render(request, 'qualtrics_link/error.html', {'request': request})
        else:
            logger.error('huid: {}, api call returned response code {}'.format(huid, str(acceptance_resp.status_code)))
            return render(request, 'qualtrics_link/error.html', {'request': request})

        enc_id = util.get_encrypted_huid(huid)
        key_value_pairs = "id={}&timestamp={}&expiration={}&firstname={}&lastname={}&email={}&UserType={}&Division={}"
        key_value_pairs = key_value_pairs.format(enc_id,
                                                 current_date,
                                                 expiration_date,
                                                 person_details.name_first,
                                                 person_details.name_last,
                                                 person_details.email_address,
                                                 person_details.role,
                                                 person_details.division)
        qualtrics_link = util.get_qualtrics_url(key_value_pairs)
        logger.info("{}\t{}\t{}\t{}".format(current_date, client_ip, person_details.role, person_details.division))

        # Update the users division and role fields of their Qualtrics profile
        util.update_user(huid, person_details.division, person_details.role)

        # The redirect line below will be how the application works if everything is good for the user.
        return redirect(qualtrics_link)

    else:
        logger.info("notauthorized\t{}\t{}\t{}\t{}".format(current_date, client_ip,
                                                           person_details.role, person_details.division))
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})


@login_required
@group_membership_restriction(settings.QUALTRICS_LINK.get('QUALTRICS_AUTH_GROUP'))
@require_http_methods(['GET'])
def internal(request):

    user_can_access = False
    client_ip = util.get_client_ip(request)

    # get the current date in the correct format i.e. '2008-07-16T15:42:51'
    current_time = time.time()
    current_date = datetime.datetime.utcfromtimestamp(current_time).strftime('%Y-%m-%dT%H:%M:%S')

    # get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
    # In this case we take the current time and add 10 minutes (600 seconds)
    expiration_date = datetime.datetime.utcfromtimestamp(current_time + 600).strftime('%Y-%m-%dT%H:%M:%S')

    # Form to allow admins to spoof other users
    if 'huid' in request.GET: # If the form has been submitted...
        # ContactForm was defined in the the previous section
        spoof_form = SpoofForm(request.GET) # A form bound to the POST data
        if spoof_form.is_valid(): # All validation rules pass
            huid = request.GET['huid']
            huid = huid.strip()
            logger.info('USER: '+str(request.user.username) + ' Spoofing: ' + huid)
            if huid == '':
                if 'spoofid' in request.session:
                    del request.session['spoofid']
                huid = request.user.username
                
    elif 'spoofid' in request.session:
        # We got here because the user accepted the tos and we needed a way to stay the spoofed user
        huid = request.session.get('spoofid')
        huid = huid.strip()
        logger.info('USER: ' + str(request.user.username) + ' Spoofing: ' + str(request.session.get('spoofid', 'None')))
        spoof_form = SpoofForm({'huid': huid.strip()})
    else:
        spoof_form = SpoofForm() # An unbound form
        huid = request.user.username
        huid = huid.strip()

    user_in_whitelist = util.is_user_in_whitelist(huid)

    if not huid.isdigit() and not user_in_whitelist:
        logger.info("xidnotauthorized\t{}\t{}".format(current_date, client_ip))
        return render(request, 'qualtrics_link/notauthorized.html', {'request': request})

    # The PersonDetails object extends the Person model with additional attributes
    person_details = util.get_person_details(huid, request)

    icommons_api = IcommonsApi()

    # Check if the user can use qualtrics or not
    # the value of user_can_access is set to False by default
    # if any of the checks here pass we set user_can_access to True
    if person_details.valid_dept or person_details.valid_school or user_in_whitelist:
        user_can_access = True
    
    if user_can_access:
        # If they are allowed to use Qualtrics, check to see if the user has accepted the terms of service    
        agreement_id = settings.QUALTRICS_LINK.get('AGREEMENT_ID')
        acceptance_resp = icommons_api.tos_get_acceptance(agreement_id, huid)
        
        if acceptance_resp.status_code == 200:
            acceptance_json = acceptance_resp.json()
            if 'agreements' in acceptance_json:
                length = len(acceptance_json['agreements'])
                if length > 0:
                    acceptance_text = acceptance_json['agreements'][0]['text']
                    request.session['spoofid'] = huid
                    return render(request, 'qualtrics_link/agreement.html', {'request': request, 'agreement': acceptance_text})
            else:
                logger.error('Received acceptance status of 200 but could not find any agreements for huid: {}'.format(huid))
                return render(request, 'qualtrics_link/error.html', {'request': request})
        else:
            logger.error('huid: {}, api call returned response code other than 200 {}'.format(acceptance_resp))
            return render(request, 'qualtrics_link/error.html', {'request': request})

        enc_id = util.get_encrypted_huid(huid)
        logline = "{}\t{}\t{}\t{}".format(current_date, client_ip, person_details.role, person_details.division)
        logger.info(logline)
        key_value_pairs = "id={}&timestamp={}&expiration={}&firstname={}&lastname={}&email={}&UserType={}&Division={}"
        key_value_pairs = key_value_pairs.format(enc_id,
                                                 current_date,
                                                 expiration_date,
                                                 person_details.name_first,
                                                 person_details.name_last,
                                                 person_details.email_address,
                                                 person_details.role,
                                                 person_details.division)
        sso_test_link = util.get_sso_test_url(key_value_pairs)
        qualtrics_link = util.get_qualtrics_url(key_value_pairs)
        context = {
            'request': request,
            'qualtricslink': qualtrics_link,
            'ssotestlink': sso_test_link,
            'huid': huid,
            'user_in_whitelist': user_in_whitelist,
            'processed_data': person_details,
            'person': person_details.person,
            'form': spoof_form
        }
        return render(request, 'qualtrics_link/main.html', context)
        
    else:
        logger.info("notauthorized\t{}\t{}\t{}\t{}".format(current_date, client_ip, person_details.role, person_details.division))
        return render(request, 'qualtrics_link/notauthinternal.html', {'request': request, 'person': person_details.person, 'processed_data': person_details})


@login_required
@require_http_methods(['GET'])
def user_accept_terms(request):
    huid = request.session.get('spoofid', False)
    if not huid:
        huid = request.user.username

    icommons_api = IcommonsApi()
    ip_address = util.get_client_ip(request)
    params = {'agreementId': '260', 'ipAddress': ip_address}
    resp = icommons_api.tos_create_acceptance(params, huid)
    
    if resp.status_code == 200:
        logger.info("termsofservice accepted: \t{}\t{}".format(ip_address, '260'))
        return redirect(settings.QUALTRICS_LINK.get('USER_ACCEPTED_TERMS_URL', 'ql:launch'))
    
    logger.error("Error accepting terms of service")
    return render(request, 'qualtrics_link/error.html', {'request': request})
    

@login_required
@require_http_methods(['GET'])
def user_decline_terms(request):
    logger.info("User declined terms of service")
    return redirect(settings.QUALTRICS_LINK.get('USER_DECLINED_TERMS_URL', 'http://surveytools.harvard.edu'))


@require_http_methods(['GET'])
def get_org_info(request):

    api_url = settings.QUALTRICS_LINK.get('QUALTRICS_API_URL')
    end_date = date.today().strftime("%Y-%m-%d")

    query = {
        'Request': 'getResponseCountsByOrganization',
        'User': settings.QUALTRICS_LINK.get('QUALTRICS_API_USER'),
        'Token': settings.QUALTRICS_LINK.get('QUALTRICS_API_TOKEN'),
        'StartDate': '2010-01-01',
        'EndDate': end_date,
        'Format': 'JSON',
        'Version': '2.0',
    }

    if 'getResponseCountsByOrganization' not in request.session:
        params = urllib.urlencode(query)
        api_response = urllib.urlopen(api_url, params)
        result = api_response.read()
        request.session['getResponseCountsByOrganization'] = result
    else:
        result = request.session.get('getResponseCountsByOrganization', '{}')

    response_counts = '{ "getResponseCountsByOrganization" : ' + result + '}'
    api_response = None

    query2 = {
        'Request': 'getOrgActivity',
        'User': settings.QUALTRICS_LINK.get('QUALTRICS_API_USER'),
        'Token': settings.QUALTRICS_LINK.get('QUALTRICS_API_TOKEN'),
        'Format': 'JSON',
        'Version': '2.0',
        'Organization': 'harvard',
    }

    if 'getOrgActivity' not in request.session:
        params = urllib.urlencode(query2)
        api_response = urllib.urlopen(api_url, params)
        result = api_response.read()
        request.session['getOrgActivity'] = result
    else:
        result = request.session.get('getOrgActivity', '{}')

    org_activity = '{ "getOrgActivity" : ' + result + '}'
    result = '{ "org_info" : [' + response_counts + ',' + org_activity + ' ]}'

    response = HttpResponse(result, content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*" 
    return response
