import hashlib
import hmac
import base64
import logging
import urllib2
from unicodedata import normalize
from Crypto.Cipher import AES
from django.conf import settings
from datetime import date
from icommons_common.models import QualtricsAccessList

logger = logging.getLogger(__name__)

BLACKLIST = set(['HBS', 'HMS', 'HSDM', 'HBP'])
AREA_LOOKUP = {
    'AAD': 'HAA (Alumni Assoc.)',
    'ADG': 'Central Administration',
    'ARB': 'Central Administration',
    'ART': 'Central Administration',
    'COL': 'FAS',
    'DCE': 'EXT',
    'DEF': 'Central Administration',
    'DES': 'GSD',
    'DIN': 'Central Administration',
    'DIV': 'HDS',
    'DOK': 'Central Administration',
    'EAS': 'FAS',
    'ECS': 'EXT',
    'EDU': 'GSE',
    'EXT': 'EXT',
    'FAS': 'FAS',
    'FCL': 'Central Administration',
    'FGS': 'FAS',
    'GSD': 'GSD',
    'GSE': 'GSE',
    'HAM': 'Central Administration',
    'HAS': 'Central Administration',
    'HBP': 'HBS',
    'HBS': 'HBS',
    'HCL': 'FAS',
    'HCU': 'Central Administration',
    'HDS': 'HDS',
    'HGR': 'Central Administration',
    'HIO': 'Central Administration',
    'HKS': 'HKS',
    'HLN': 'Central Administration',
    'HLS': 'HLS',
    'HMC': 'Central Administration',
    'HMS': 'HMS',
    'HRE': 'Central Administration',
    'HSDM': 'HSDM',
    'HSPH': 'HSPH',
    'HUIT': 'HUIT',
    'HUL': 'Central Administration',
    'HUP': 'Central Administration',
    'HUS': 'Central Administration',
    'HVN': 'Central Administration',
    'INI': 'Central Administration',
    'KSG': 'HKS',
    'LAS': 'Central Administration',
    'LAW': 'HLS',
    'LHF': 'Central Administration',
    'MAG': 'Central Administration',
    'MAR': 'Central Administration',
    'MEM': 'Central Administration',
    'NIE': 'Central Administration',
    'Not Available': 'Other',
    'OGB': 'Central Administration',
    'OGC': 'Central Administration',
    'OHR': 'Central Administration',
    'OPR': 'Central Administration',
    'Other': 'Other',
    'PAI': 'Central Administration',
    'POL': 'Central Administration',
    'RAD': 'Radcliffe',
    'SAO': 'Central Administration',
    'SDM': 'HSDM',
    'SPH': 'HSPH',
    'SUM': 'EXT',
    'TBD': 'Central Administration',
    'UHS': 'Central Administration',
    'UIS': 'HUIT',
    'UNP': 'Central Administration',
    'UOS': 'Central Administration',
    'UPO': 'Central Administration',
    'VIT': 'Central Administration',
    'VPA': 'Central Administration',
    'VPF': 'Central Administration',
    'VPG': 'Central Administration',
} 

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 


def get_encrypted_huid(huid):
    hasher = hashlib.md5()
    hasher.update(huid)
    encid = hasher.hexdigest()
    return encid


def create_encoded_token(key_value_pairs):
    key = settings.QUALTRICS_LINK.get('QUALTRICS_APP_KEY')
    secret = bytes(key)
    key_value_pairs = normalize('NFKD', key_value_pairs).encode('ascii', 'ignore')
    data = bytes(key_value_pairs)
    encoded = base64.b64encode(hmac.new(secret, data).digest())
    token = key_value_pairs+'&mac='+encoded
    raw = pad(token)
    cipher = AES.new(key, AES.MODE_ECB)
    encoded_token = base64.b64encode(cipher.encrypt(raw))
    return urllib2.quote(encoded_token.encode("utf8"), '')


def get_sso_test_url(key_value_pairs):
    key = settings.QUALTRICS_LINK.get('QUALTRICS_APP_KEY')
    encoded_token = create_encoded_token(key_value_pairs)
    sso_test_link = 'https://new.qualtrics.com/ControlPanel/ssoTest.php?key='+key+'&mac=md5&ssotoken='+encoded_token
    return sso_test_link


def get_qualtrics_url(key_value_pairs):
    encoded_token = create_encoded_token(key_value_pairs)
    qualtrics_url = 'https://harvard.qualtrics.com/ControlPanel/?ssotoken='+encoded_token
    logger.debug("qualtrics url is %s", qualtrics_url)
    return qualtrics_url


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address


# Find the area for the given unit, if no matches then use 'Other'
def lookup_unit(unit):
    if unit in AREA_LOOKUP:
        return AREA_LOOKUP[unit]
    else:
        logger.info('unit not found: {}'.format(unit))
        return 'Other'


# Determine If the given unit is contained in the Blacklist, if it is then it is not valid.
def is_unit_valid(unit):
    return unit not in BLACKLIST


# Return the first school from the given school list that is not contained within the blacklist.
def get_valid_school(schools):
    for school_code in schools:
        school = lookup_unit(school_code)
        if school not in BLACKLIST:
            return school


# If department is not in the blacklist then return it's division, else return None
def get_valid_dept(dept):
    division = lookup_unit(dept)
    if division not in BLACKLIST:
        return division


# Determines if the Person with the given HUID is in the whitelist and the Person's expiration is today or greater.
def is_user_in_whitelist(huid):
    try:
        person = QualtricsAccessList.objects.get(user_id=huid)
        if person.expiration_date:
            if person.expiration_date >= date.today():
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
        logger.info('The HUID {} does not exist within the Qualtrics access list.'.format(huid))
        return False


def build_user_dict(data):

    user_data = {
        'role': 'generic',
        'division': 'Other',
        'validschool': False,
        'validdept': False
    }

    if 'people' in data:
        person = data['people'][0]
        
        user_data['firstname'] = person.get('firstName', 'Not Available')
        user_data['lastname'] = person.get('lastName', 'Not Available')
        user_data['email'] = person.get('email', 'Not Available')

        # School Affiliations check
        school_affiliations = person.get('schoolAffiliations', 'Not Available')

        valid_school_code = get_valid_school(school_affiliations)
        if valid_school_code is not None:
            user_data['validschool'] = True
            user_data['role'] = 'student'
            user_data['division'] = valid_school_code

        # Department Affiliations check
        department_affiliation = person.get('departmentAffiliation', 'Not Available')
        if department_affiliation.lower() != 'not available':
            valid_department = get_valid_dept(department_affiliation)
            if valid_department is not None:
                user_data['validdept'] = True
                user_data['role'] = 'employee'
                user_data['division'] = valid_department

    return user_data
