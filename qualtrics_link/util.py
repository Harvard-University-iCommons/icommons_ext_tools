#
# util.py
import hashlib
import hmac
import base64
import logging
import urllib2
from Crypto.Cipher import AES
from django.conf import settings
from datetime import date
from icommons_common.models import QualtricsAccessList

logger = logging.getLogger(__name__)

BLACKLIST = set(['HBS', 'HMS', 'HSDM', 'HBP'])
AREA_LOOKUP = {
    'AAD' : 'HAA (Alumni Assoc.)',
    'ADG' : 'Central Administration',
    'ARB' : 'Central Administration',
    'ART' : 'Central Administration',
    'COL' : 'FAS',
    'DCE' : 'EXT',
    'DEF' : 'Central Administration',
    'DES' : 'GSD',
    'DIN' : 'Central Administration',
    'DIV' : 'HDS',
    'DOK' : 'Central Administration',
    'EAS' : 'FAS',
    'EAS' : 'FAS', 
    'ECS' : 'EXT',
    'EDU' : 'GSE',
    'EXT' : 'EXT',
    'FAS' : 'FAS',
    'FCL' : 'Central Administration',
    'FGS' : 'FAS',
    'GSD' : 'GSD',
    'GSE' : 'GSE',
    'HAM' : 'Central Administration',
    'HAS' : 'Central Administration',
    'HBP' : 'HBS',
    'HBS' : 'HBS',
    'HCL' : 'FAS',
    'HCU' : 'Central Administration',
    'HDS' : 'HDS',
    'HGR' : 'Central Administration',
    'HIO' : 'Central Administration',
    'HKS' : 'HKS',
    'HLN' : 'Central Administration',
    'HLS' : 'HLS',
    'HMC' : 'Central Administration',
    'HMS' : 'HMS',
    'HRE' : 'Central Administration',
    'HSDM' : 'HSDM',
    'HSPH' : 'HSPH',
    'HUIT' : 'HUIT',
    'HUL' : 'Central Administration',
    'HUP' : 'Central Administration',
    'HUS' : 'Central Administration',
    'HVN' : 'Central Administration',
    'INI' : 'Central Administration',
    'KSG' : 'HKS',
    'LAS' : 'Central Administration',
    'LAW' : 'HLS',
    'LHF' : 'Central Administration',
    'MAG' : 'Central Administration',
    'MAR' : 'Central Administration',
    'MEM' : 'Central Administration',
    'NIE' : 'Central Administration',
    'Not Available' : 'Other',
    'OGB' : 'Central Administration',
    'OGC' : 'Central Administration',
    'OHR' : 'Central Administration',
    'OPR' : 'Central Administration',
    'Other' : 'Other',
    'PAI' : 'Central Administration',
    'POL' : 'Central Administration',
    'RAD' : 'Radcliffe',
    'SAO' : 'Central Administration',
    'SDM' : 'HSDM',
    'SPH' : 'HSPH',
    'SPH' : 'HSPH',
    'SUM' : 'EXT',
    'TBD' : 'Central Administration',
    'UHS' : 'Central Administration',
    'UIS' : 'HUIT',
    'UNP' : 'Central Administration',
    'UOS' : 'Central Administration',
    'UPO' : 'Central Administration',
    'VIT' : 'Central Administration',
    'VPA' : 'Central Administration',
    'VPF' : 'Central Administration',
    'VPG' : 'Central Administration',
} 

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 

def getencryptedhuid(huid):
    hasher = hashlib.md5()
    hasher.update(huid)
    encid = hasher.hexdigest()
    return encid

def createencodedtoken(keyvaluepairs):
    key = settings.QUALTRICS_LINK.get('QUALTRICS_APP_KEY')
    secret = bytes(key)
    data = bytes(keyvaluepairs)
    encoded = base64.b64encode(hmac.new(secret, data).digest())
    token = keyvaluepairs+'&mac='+encoded 
    raw = pad(token)
    cipher = AES.new(key, AES.MODE_ECB)
    encodedtoken = base64.b64encode(cipher.encrypt(raw))
    return urllib2.quote(encodedtoken.encode("utf8"),'') 

def getssotesturl(keyvaluepairs):
    key = settings.QUALTRICS_LINK.get('QUALTRICS_APP_KEY')
    encodedtoken = createencodedtoken(keyvaluepairs)
    ssotestlink = 'https://new.qualtrics.com/ControlPanel/ssoTest.php?key='+key+'&mac=md5&ssotoken='+encodedtoken
    return ssotestlink

def getqualtricsurl(keyvaluepairs):
    encodedtoken = createencodedtoken(keyvaluepairs)
    qualtricsurl = 'https://harvard.qualtrics.com/ControlPanel/?ssotoken='+encodedtoken
    print qualtricsurl
    return qualtricsurl

def getclientip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipaddress = x_forwarded_for.split(',')[0]
    else:
        ipaddress = request.META.get('REMOTE_ADDR')
    return ipaddress

def lookupunit(unit):
    if unit in AREA_LOOKUP:
        return AREA_LOOKUP[unit]
    else:
        logger.info('unit not found: {}'.format(unit))
        return 'Other'

def isunitvalid(unit):
    if unit not in BLACKLIST:
        return True
    return False

def getvalidschool(schools):
    for schoolcode in schools:
        school = lookupunit(schoolcode)
        if school not in BLACKLIST:
            return school

def getvaliddept(dept):
    division = lookupunit(dept)
    if division not in BLACKLIST:
        return division

def isuserinwhitelist(huid):
    try:
        person = QualtricsAccessList.objects.get(user_id=huid)
        if person.expiration_date:
            expiration_date = person.expiration_date   
            if expiration_date >= date.today():
                # the user is in the whitelist and has an expiration date that is valid
                return True
            else:
                # the user is in the whitelist and has an expiration date that has expired
                return False
        else:
            # the user is in the whitelist but has no expiration date
            return True
    except QualtricsAccessList.DoesNotExist:
        # the user is not in the whitelist'
        return False

def builduserdict(data):

    userdata = {}
    
    userdata['role'] = 'generic'
    userdata['division'] = 'Other'
    userdata['validschool'] = False
    userdata['validdept'] = False
    #userdata['schoolaffiliations'] = None
    #userdata['departmentaffiliation'] = None
    #userdata['personaffiliation'] = None
    
    if 'people' in data:
        person = data['people'][0]
        
        userdata['firstname'] = person.get('firstName', 'Not Available')
        userdata['lastname'] = person.get('lastName', 'Not Available')
        userdata['email'] = person.get('email', 'Not Available')

        #Person Affiliations check
        #personaffiliation = person.get('personAffiliation', 'Not Available')
        #if personaffiliation.lower() != 'not available':
            #userdata['personaffiliation'] = personaffiliation
            #userdata['role'] = personaffiliation

        #School Affiliations check    
        schoolaffiliations = person.get('schoolAffiliations', 'Not Available')

        #userdata['schoolaffiliations'] = schoolaffiliations
        valid_school_code = getvalidschool(schoolaffiliations)
        if valid_school_code is not None:
            userdata['validschool'] = True
            userdata['role'] = 'student'
            userdata['division'] = valid_school_code

        # Department Affiliations check
        departmentaffiliation = person.get('departmentAffiliation', 'Not Available')
        if departmentaffiliation.lower() != 'not available':
            #userdata['departmentaffiliation'] = departmentaffiliation
            valid_department = getvaliddept(departmentaffiliation)
            if valid_department is not None:
                userdata['validdept'] = True
                userdata['role'] = 'employee'
                userdata['division'] = valid_department

      
    return userdata
