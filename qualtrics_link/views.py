import datetime
import logging
import time
import urllib
from datetime import date
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from icommons_common.auth.decorators import group_membership_restriction
from icommons_common.monitor.views import BaseMonitorResponseView

import qualtrics_link.util as util
from qualtrics_link.forms import SpoofForm
from qualtrics_link.models import Acceptance

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
    person_details = util.get_person_details(huid)

    if person_details is None:
        logger.error('No records with the huid of {} could be found'.format(huid))
        return render(request, 'qualtrics_link/error.html', {'request': request})

    # Check if the user can use qualtrics or not
    # the value of user_can_access is set to False by default
    # if any of the checks here pass we set user_can_access to True
    if person_details.valid_dept or person_details.valid_school or user_in_whitelist:
        user_can_access = True

    if user_can_access:
        # Check to see if the user has accepted the terms of service

        user_acceptance = None
        try:
            user_acceptance = Acceptance.objects.get(user_id=huid)
        except Acceptance.DoesNotExist:
            logger.info('User %s has not  accepted term of service ', huid)
        except:
            logger.error('Exception in checking for user acceptance, '
                         'user_id:%s', huid)
            return render(request, 'qualtrics_link/error.html')

        #  Render agreement page if user has not accepted term of service
        if not user_acceptance:
            return render(request, 'qualtrics_link/agreement.html',
                          {'request': request})

        enc_id = util.get_encrypted_huid(huid)
        key_value_pairs = u"id={}&timestamp={}&expiration={}&firstname={}&lastname={}&email={}&UserType={}&Division={}"
        key_value_pairs = key_value_pairs.format(enc_id,
                                                 current_date,
                                                 expiration_date,
                                                 person_details.first_name,
                                                 person_details.last_name,
                                                 person_details.email,
                                                 person_details.role,
                                                 util.DIVISION_MAPPING[person_details.division])
        qualtrics_link = util.get_qualtrics_url(key_value_pairs)
        logger.info("{}\t{}\t{}\t{}".format(current_date, client_ip, person_details.role, person_details.division))

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
    person_details = util.get_person_details(huid)

    if person_details is None:
        logger.error('No records with the huid of {} could be found'.format(huid))
        return render(request, 'qualtrics_link/error.html', {'request': request})

    # Check if the user can use qualtrics or not
    # the value of user_can_access is set to False by default
    # if any of the checks here pass we set user_can_access to True
    if person_details.valid_dept or person_details.valid_school or user_in_whitelist:
        user_can_access = True
    
    if user_can_access:
        # If they are allowed to use Qualtrics, check to see if the user has accepted the terms of service
        user_acceptance = None
        try:
            user_acceptance = Acceptance.objects.get(user_id=huid)
        except Acceptance.DoesNotExist:
            logger.info('User %s has not  accepted term of service ', huid)
        except Exception as e:
            logger.error('Exception in checking for user acceptance, '
                     'user_id:%s', huid, e)
            return render(request, 'qualtrics_link/error.html')

        #  Render agreement page if user has not accepted term of service
        if not user_acceptance:
            request.session['spoofid'] = huid
            return render(request, 'qualtrics_link/agreement.html',
                          {'request': request})


        enc_id = util.get_encrypted_huid(huid)
        logline = "{}\t{}\t{}\t{}".format(current_date, client_ip, person_details.role, person_details.division)
        logger.info(logline)
        key_value_pairs = u"id={}&timestamp={}&expiration={}&firstname={}&lastname={}&email={}&UserType={}&Division={}"
        key_value_pairs = key_value_pairs.format(enc_id,
                                                 current_date,
                                                 expiration_date,
                                                 person_details.first_name,
                                                 person_details.last_name,
                                                 person_details.email,
                                                 person_details.role,
                                                 util.DIVISION_MAPPING[person_details.division])
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
        context = {
            'request': request,
            'person': person_details.person,
            'processed_data': person_details,
            'huid': huid,
            'user_in_whitelist': user_in_whitelist,
        }
        logger.info("notauthorized\t{}\t{}\t{}\t{}".format(current_date, client_ip, person_details.role, person_details.division))
        return render(request, 'qualtrics_link/notauthinternal.html', context)


@login_required
@require_http_methods(['GET'])
def user_accept_terms(request):
    huid = request.session.get('spoofid', False)
    if not huid:
        huid = request.user.username

    ip_address = util.get_client_ip(request)
    try:

        user_acceptance = Acceptance.objects.create(
            user_id=huid,
            ip_address=ip_address,
            acceptance_date=timezone.now()
        )
        logger.info("termsofservice accepted: \t{}".format(ip_address))
        return redirect(settings.QUALTRICS_LINK.get('USER_ACCEPTED_TERMS_URL', 'ql:launch'))
    except Exception as e:
        logger.error('Exception saving acceptance for user',e)

    return render(request, 'qualtrics_link/error.html', {'request': request})
    

@login_required
@require_http_methods(['GET'])
def user_decline_terms(request):
    logger.info("User declined terms of service")
    return redirect(settings.QUALTRICS_LINK.get('USER_DECLINED_TERMS_URL'))


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
