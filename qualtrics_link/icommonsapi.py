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

    def __init__(self):
        self.sslsession = requests.Session()
        self.sslsession.mount('https://', MyAdapter())

    def getpersondata(self, huid):
        peopleurl = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'people/by_id/'+huid+'.json'
        #peoplesession = requests.Session()
        #peoplesession.mount('https://', MyAdapter())
        resp = self.sslsession.get(peopleurl, verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], \
        	settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return resp

    def getpersongroupdata(self, huid):
        group_url = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'groups/membership_by_user/'+huid+'.json'
        #group_session = requests.Session()
        #group_session.mount('https://', MyAdapter())
        group_resp = self.sslsession.get(group_url, verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], \
            settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return group_resp

    def getuseracceptance(self, agreementid, huid):
        acceptance_url = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'policy_agreement/acceptance/'+agreementid+'/'+huid+'.json'
        #acceptance_session = requests.Session()
        #acceptance_session.mount('https://', MyAdapter())
        acceptance_resp = self.sslsession.get(acceptance_url, verify=False, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], \
        	settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return acceptance_resp

    def create_acceptance(self, params, huid):
        #data = json.dumps(params)
        useracceptanceurl = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']+'policy_agreement/create_acceptance/'+huid
        #sslsession = requests.Session()
        #sslsession.mount('https://', MyAdapter())
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        resp = self.sslsession.post(useracceptanceurl, verify=False, \
            data=params, headers=headers, auth=(settings.ICOMMONS_COMMON['ICOMMONS_API_USER'], settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']))
        return resp

