#
# iCommonsapi

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from django.views.decorators.http import require_http_methods
from django.conf import settings
import ssl
import requests 
import logging

class MyAdapter(HTTPAdapter):
# We need to subclass the HttpAdater class to allow connections
# to SSL version 1. 
    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

class IcommonsApi(object):

    def __init__(self, huid):
        self.huid = huid

    def getpersondata(self):
        peopleurl = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'people/by_id/'+self.huid+'.json'
        peoplesession = requests.Session()
        peoplesession.mount('https://', MyAdapter())
        resp = peoplesession.get(peopleurl, verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], \
        	settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return resp

    def getpersongroupdata(self):
        group_url = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'groups/membership_by_user/'+self.huid+'.json'
        group_session = requests.Session()
        group_session.mount('https://', MyAdapter())
        group_resp = group_session.get(group_url, verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], \
            settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return group_resp

    def getuseracceptance(self, agreementid):
        acceptance_url = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'policy_agreement/acceptance/'+agreementid+'/'+self.huid+'.json'
        acceptance_session = requests.Session()
        acceptance_session.mount('https://', MyAdapter())
        acceptance_resp = acceptance_session.get(acceptance_url, verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], \
        	settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return acceptance_resp

    def create_acceptance(self, params):
        #data = json.dumps(params)
        useracceptanceurl = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'policy_agreement/create_acceptance/'+self.huid
        sslsession = requests.Session()
        sslsession.mount('https://', MyAdapter())
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        resp = sslsession.post(useracceptanceurl, verify=False, \
            data=params, headers=headers, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return resp

