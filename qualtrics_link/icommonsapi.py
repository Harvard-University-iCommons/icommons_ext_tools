#
# iCommonsapi

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from django.views.decorators.http import require_http_methods
from django.conf import settings
import ssl
import requests 
import logging

# this is handy for debugging requests
#import httplib
#httplib.HTTPConnection.debuglevel = 1

logger = logging.getLogger(__name__)

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
        self.host = settings.ICOMMONS_COMMON['ICOMMONS_API_HOST']
        self.username = settings.ICOMMONS_COMMON['ICOMMONS_API_USER']
        self.password = settings.ICOMMONS_COMMON['ICOMMONS_API_PASS']

    def getpersondata(self, huid):
        url = self.host+'people/by_id/'+huid+'.json'
        #peoplesession = requests.Session()
        #peoplesession.mount('https://', MyAdapter())
        logger.debug('API CALL: '+url)
        resp = self.sslsession.get(url, verify=False, auth=(self.username, self.password))
        return resp

    def getpersongroupdata(self, huid):
        url = self.host+'groups/membership_by_user/'+huid+'.json'
        #group_session = requests.Session()
        #group_session.mount('https://', MyAdapter())
        logger.debug('API CALL: '+url)
        group_resp = self.sslsession.get(url, verify=False, auth=(self.username, self.password))
        return group_resp

    def getuseracceptance(self, agreementid, huid):
        url = self.host+'policy_agreement/acceptance/'+agreementid+'/'+huid+'.json'
        #acceptance_session = requests.Session()
        #acceptance_session.mount('https://', MyAdapter())
        logger.debug('API CALL: '+url)
        acceptance_resp = self.sslsession.get(url, verify=False, auth=(self.username, self.password))
        return acceptance_resp

    def create_acceptance(self, params, huid):
        #data = json.dumps(params)
        url = self.host+'policy_agreement/create_acceptance/'+huid
        #sslsession = requests.Session()
        #sslsession.mount('https://', MyAdapter())
        logger.debug('API CALL: '+url)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        resp = self.sslsession.post(url, verify=False, \
            data=params, headers=headers, auth=(self.username, self.password))
        return resp

