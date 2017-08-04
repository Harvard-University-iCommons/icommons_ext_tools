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
from icommons_common.models import Person
import requests
from django.shortcuts import render

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


# Get correct person record from the given person list
def filter_person_list(person_list):
    for person in person_list:
        # Do the filtering logic here to return the correct person record
        return person


# Get the person list matching the given HUID or return None
# If no matching Person records, return the error page.
def get_person_list(huid, request):
    person_list = Person.objects.filter(huid=huid, prime_role_indicator='Y')

    if len(person_list) == 0:
        logger.error('The person with huid {} could not be found')
        return render(request, 'qualtrics_link/error.html', {'request': request})
    else:
        return person_list


# Get the list of people for the given id and then pass it to the filtering function
def get_correct_person(huid, request):
    person_list = get_person_list(huid, request)
    return filter_person_list(person_list)


# Will update the current role and division of the given HUID user
def update_user(huid, request):
    person = get_correct_person(huid, request)
    person_details = get_person_details(person)

    key = settings.QUALTRICS_LINK.get('QUALTRICS_APP_KEY')
    req_params = {
        'divisionId': person_details.division,
        'userType': person_details.role
    }

    requests.put(url='https://harvard.qualtrics.com/API/v3/users/:{}'.format(huid),
                 data=req_params,
                 headers={'X-API-TOKEN': key})


# Data structure to extend the Person model and add extra attributes
class PersonDetails:
    def __init__(self, first_name, last_name, email, role='student',
                 division='Other', valid_school=False, valid_dept=False):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role
        self.division = division
        self.valid_school = valid_school
        self.valid_dept = valid_dept


# Creates a PersonDetails instance by using the given person record to get values for the extended fields
def get_person_details(person):

    # TODO Apply appropriate logic to set values or call separate functions to get values
    role = ''  # get_role(person)
    division = ''  # get_division(person)
    valid_school = False
    valid_dept = False

    return PersonDetails(first_name=person.name_first,
                         last_name=person.name_last,
                         email=person.email_address,
                         role=role,
                         division=division,
                         valid_school=valid_school,
                         valid_dept=valid_dept)


