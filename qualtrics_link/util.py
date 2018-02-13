import base64
import hashlib
import hmac
import logging
import urllib2
from datetime import date
from unicodedata import normalize

import requests
from Crypto.Cipher import AES
from django.conf import settings

from icommons_common.models import Person
from icommons_common.models import QualtricsAccessList
from qualtrics_link.models import SchoolCodeMapping

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

# Mapping of a division to its Qualtrics ID
DIVISION_MAPPING = {
    'FAS': 'DV_0uG93Am70qIFb00',
    'GSE': 'DV_eesMPIncvHA270U',
    'HSPH': 'DV_cvfNy3UwERh9IcA',
    'Other': 'DV_1zu8x43ZIyqzWlu',
    'HKS': 'DV_bdu3uP2WTYThpOY',
    'EXT': 'DV_cSx7CCmUZ1DaS3i',
    'HLS': 'DV_6DN9Q7jTRzsxgHy',
    'HUIT': 'DV_77MUQ7NsyaGcQU4',
    'GSD': 'DV_7V89XC1uxWU2ODW',
    'Central Administration': 'DV_6Fhm425s7ozZM5D',
    'HDS': 'DV_5o8WAy3WJXLNX2Q',
    'HAA (Alumni Assoc.)': 'DV_1WSu6zRMeNx6ZYU',
    'VPAL Research and Affiliates': 'DV_8dpaRpPHqefdNAx',
    'Berkman': 'DV_1Ro0atRhq0UV9ti',
    'Radcliffe': 'DV_agzgkeDIaZPEJHD',
    'API Div': 'DV_23NVy6XjBHhOXxX',
    'GSE-PPE [no longer used]': 'DV_0vsxWeIjXJWeS21'
}

# Maps the user type to its equivalent Qualtrics ID
USER_TYPE_MAPPING = {
    'employee': 'UT_egutew4nqz71QgI',
    'student': 'UT_787UadC574xhxgU',
    'brand administrator': 'UT_BRANDADMIN'
}


# Choice tuple used in the Qualtrics internal admin form
DIVISION_CHOICES = (
    ('API Div', 'API Div'),
    ('Berkman', 'Berkman'),
    ('Central Administration', 'Central Administration'),
    ('EXT', 'EXT'),
    ('FAS', 'FAS'),
    ('GSE', 'GSE'),
    ('GSD', 'GSD'),
    ('HAA (Alumni Assoc.)', 'HAA (Alumni Assoc.)'),
    ('HDS', 'HDS'),
    ('HKS', 'HKS'),
    ('HLS', 'HLS'),
    ('HSPH', 'HSPH'),
    ('HUIT', 'HUIT'),
    ('Other', 'Other'),
    ('Radcliffe', 'Radcliffe'),
    ('VPAL Research and Affiliates', 'VPAL Research and Affiliates')
)

ROLE_CHOICES = (
    ('employee', 'Employee'),
    ('student', 'Student')
)

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
    token = key_value_pairs + '&mac=' + encoded
    raw = pad(token)
    cipher = AES.new(key, AES.MODE_ECB)
    encoded_token = base64.b64encode(cipher.encrypt(raw))
    return urllib2.quote(encoded_token.encode("utf8"), '')


def get_sso_test_url(key_value_pairs):
    key = settings.QUALTRICS_LINK.get('QUALTRICS_APP_KEY')
    encoded_token = create_encoded_token(key_value_pairs)
    sso_test_link = 'https://new.qualtrics.com/ControlPanel/ssoTest.php?key=' + key + '&mac=md5&ssotoken=' + encoded_token
    return sso_test_link


def get_qualtrics_url(key_value_pairs):
    encoded_token = create_encoded_token(key_value_pairs)
    qualtrics_url = 'https://harvard.qualtrics.com/ControlPanel/?ssotoken=' + encoded_token
    logger.debug("qualtrics url is %s", qualtrics_url)
    return qualtrics_url


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address


def lookup_unit(unit):
    """
    Find the area for the given unit, if no matches then use 'Other'
    """
    if unit in AREA_LOOKUP:
        return AREA_LOOKUP[unit]
    else:
        logger.info('unit not found: {}'.format(unit))
        return 'Other'


def is_unit_valid(unit):
    """
    Determine If the given unit is contained in the Blacklist, if it is then it is not valid
    """
    return unit not in BLACKLIST


def get_valid_school(schools):
    """
    Return the first school from the given school list that is not contained within the blacklist
    """
    for school_code in schools:
        school = lookup_unit(school_code)
        if school not in BLACKLIST:
            return school


def get_valid_dept(dept):
    """
    If department is not in the blacklist then return it's division, else return None
    """
    division = lookup_unit(dept)
    if division not in BLACKLIST:
        return division


def is_user_in_whitelist(huid):
    """
    Determines if the Person with the given HUID is in the whitelist and the Person's expiration is today or greater
    """
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


def get_person_with_prime_indicator(person_list):
    """
    Iterate over a person list and return the first person with prime_role_indicator set to 'Y'
    Will return None if this condition is not met 
    """
    for person in person_list:
        if person.prime_role_indicator == 'Y':
            return person


def filter_person_list(person_list):
    """
    If there are more than one record returned for a HUID, we want to determine if they contain attributes with priority
     - Employee
        - If multiple Employee records for HUID, check if the prime role indicator field is set for any of them
     - Person with prime role indicator field set to 'Y'
     - If no matches are made for the above conditions, return the first person in the given list.   
    """

    # Employee check
    employee_list = []
    for person in person_list:
        if person.role_type_cd.lower() == 'employee':
            employee_list.append(person)

    # If more than one Person with Employee role, check if any have prime indicator set to 'Y'
    # Else return the first employee record
    if len(employee_list) > 0:
        emp_with_prime = get_person_with_prime_indicator(employee_list)
        if emp_with_prime is not None:
            return emp_with_prime
        else:
            return employee_list[0]

    # Check if any of the Person records contain the prime role indicator
    person_with_prime = get_person_with_prime_indicator(person_list)
    if person_with_prime is not None:
        return person_with_prime

    # If no employee records were found, then return the first person in the list
    return person_list[0]


def get_person_list(huid):
    """
    Get the person list matching the given HUID
    """
    person_list = Person.objects.filter(univ_id=huid)
    return person_list


def update_qualtrics_user(user_id, division, role):
    """
    This function is waiting on a Qualtrics API update to be able to get a user by their username
    Will update the given HUID users current role and division for their Qualtrics account
    """
    try:
        token = settings.QUALTRICS_LINK.get('QUALTRICS_API_TOKEN')
        req_params = {
            'divisionId': division,
            'userType': role
        }

        return requests.put(url='https://harvard.az1.qualtrics.com/API/v3/users/{}'.format(user_id),
                            json=req_params,
                            headers={'X-API-TOKEN': token,
                                     'content-type': 'application/json'})
    except Exception as e:
        logger.warning('An error occurred while making a Qualtrics update call. '
                       'ID: %s, Division: %s, Role: %s') % (user_id, division, role)
        logger.warning(e)
        return {'meta': {'httpStatus': '500'}}


def get_qualtrics_user(huid):
    """
    This function is waiting on a Qualtrics API update to be able to get a user by their username
    Query Qualtrics to get the user with the given HUID
    """
    enc_id = get_encrypted_huid(huid)
    token = settings.QUALTRICS_LINK.get('QUALTRICS_API_TOKEN')
    response = requests.get(url='https://harvard.qualtrics.com/API/v3/users/{}'.format(enc_id),
                            headers={'X-API-TOKEN': token})
    return response


def get_all_qualtrics_users(url='https://harvard.qualtrics.com/API/v3/users/'):
    """
    Gets all the Qualtrics accounts as a json object
    If a URL is supplied, then it will be providing pagination of the nextPage field from the previous call
    """
    token = settings.QUALTRICS_LINK.get('QUALTRICS_API_TOKEN')
    response = requests.get(url=url, headers={'X-API-TOKEN': token})
    return response.json()


def lookup_school_affiliations(school_cd):
    """
    Maps the given school code to a school using the school_code_mapping table  
    """
    try:
        return SchoolCodeMapping.objects.get(student_school_code=school_cd).employee_school_code
    except SchoolCodeMapping.DoesNotExist:
        logging.error('The school code {} could not be found.'.format(school_cd))
        return 'Not Available'


def get_school_affiliations(person_list):
    """
    Gets the list of school codes for each person in the given list
    """
    affiliations = []
    for person in person_list:
        school = 'Not Available'
        # Only lookup a school affiliation if the person has a school code
        if person.school_cd != '' and person.school_cd is not None:
            school = lookup_school_affiliations(person.school_cd)

        if school != '' and school != 'Not Available':
            affiliations.append(str(school))

    return affiliations


class PersonDetails:
    """
    Data structure to extend the Person model and add extra attributes
    """

    def __init__(self, person, id, first_name, last_name, email, role='student',
                 division='Other', valid_school=False, valid_dept=False,
                 school_affiliations=[]):
        self.person = person
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role
        self.division = division
        self.valid_school = valid_school
        self.valid_dept = valid_dept
        self.school_affiliations = school_affiliations,


def get_person_details(huid, person_list=None):
    """
    Creates a PersonDetails instance by using the given person record to get values for the extended fields.
    If the optional person_list is passed in, it avoids having to redo a query
    """
    if person_list is None:
        person_list = get_person_list(huid)

    if len(person_list) > 0:
        person = filter_person_list(person_list)
    else:
        return None

    role = 'student'
    division = 'Other'
    valid_school = False
    valid_dept = False

    # School Affiliations check
    school_affiliations = get_school_affiliations(person_list)
    valid_school_code = get_valid_school(school_affiliations)
    if valid_school_code is not None:
        valid_school = True
        division = valid_school_code

    # Department Affiliations check
    if person.department != '':
        valid_dept_name = get_valid_dept(person.department)
        if valid_dept_name is not None:
            valid_dept = True
            role = 'employee'
            division = valid_dept_name

    return PersonDetails(person=person,
                         id=person.univ_id,
                         first_name=person.name_first,
                         last_name=person.name_last,
                         email=person.email_address,
                         role=role,
                         division=division,
                         valid_school=valid_school,
                         valid_dept=valid_dept,
                         school_affiliations=school_affiliations)
