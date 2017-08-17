from django.core.management.base import BaseCommand, CommandError
import pprint
import logging
from qualtrics_link import util
from qualtrics_link.models import SchoolCodeMapping
from icommons_common.models import Person
import json
import pickle


logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


class Command(BaseCommand):
    help = 'Help text'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='helper text placeholder')
        parser.add_argument('--get-users', action='store_true', help='Query Qualtrics to get all users and store them '
                                                                     'in a data.json file.')
        parser.add_argument('--perform-update', action='store_true', help='Perform the update of Qualtrics user using '
                                                                          'the filtered list file.')
        parser.add_argument('--filter-users', action='store_true', help='Filters the data.json file to produce a new'
                                                                       'file containing only users that need to be '
                                                                       'updated.')
        parser.add_argument('--stats', action='store_true', help='')

    def handle(self, *args, **options):
        if options['get_users']:
            self.get_users()
        if options['filter_users']:
            self.filter_users()
        elif options['stats']:
            self.stats()
        else:
            print 'You need to select a valid option'

    @staticmethod
    def stats():
        data_file = open('data.json', 'r')
        data = json.load(data_file)

        total_users = len(data)

        print 'Amount of users: %d' % total_users

        count = 0
        for person in data:
            if person['accountStatus'] == 'active':
                count += 1

        print 'Total active users: %d' % count
        print 'Total inactive users: %d' % (total_users - count)


    def update_users(self):
        """
        Will go through the list of users in the filtered file and update the users information via the Qualtrics API.
        """
        pass


    @staticmethod
    def filter_users():
        employee_user_type = 'UT_egutew4nqz71QgI'
        student_user_type = 'UT_787UadC574xhxgU'
        brand_admin = 'UT_BRANDADMIN'
        user_type_list = [employee_user_type, student_user_type, brand_admin]

        # Mapping of a division to its Qualtrics ID
        division_mapping = {
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

        data_file = open('data.json', 'r')
        data = json.load(data_file)
        print('%d records in file' % len(data))

        # List of all users that need to be updated
        update_list = []

        # How many users to process at each run time.
        slice_amount = 15

        for q_person in data[:slice_amount]:
            q_id = q_person['id']
            q_username = q_person['username']
            q_division = q_person['divisionId']
            q_role = q_person['userType']
            q_email = q_person['email']
            q_first_name = q_person['firstName']
            q_last_name = q_person['lastName']

            # If the Qualtrics user has no email, filter based on first and last name
            if q_email is None:
                person_queryset = Person.objects.filter(name_first=q_first_name, name_last=q_last_name)
            else:
                person_queryset = Person.objects.filter(email_address=q_email)

            matching_person = None
            # Iterate through the queryset, encrypting the current Persons HUID to find a match with the q_id
            for person in person_queryset:
                enc_id = util.get_encrypted_huid(person.univ_id) + '#harvard'
                if enc_id == q_username:
                    matching_person = person
                    break

            # Compare the Qualtrics data against the LDAP People data
            if matching_person is not None:
                person_details = util.get_person_details(matching_person.univ_id)
                p_role = person_details.role
                p_division = division_mapping[person_details.division]

                update_person = False
                update_dict = {
                    'user_id': q_id
                }
                # Do the comparison of what is currently in Qualtrics and what the matching person has
                # If they differ, then add to the filtered list the current persons q_id, role and division
                if p_division != q_division:
                    update_dict['division'] = p_division
                    update_person = True

                # If the Person is not a Student or Employee, then they need to be updated
                if q_role not in user_type_list:
                    update_dict['user_type'] = p_role
                    update_person = True

                # If the update person bool has been set to True, then get the values from the update dict to be
                # added to the update list. Provide the person
                if update_person:
                    # TODO make check for brand admin

                    update_entry = {
                        'user_id': update_dict.get('user_id'),
                        'division': update_dict.get('division', p_division),
                        'role': update_dict.get('role', p_role)
                    }

                    print
                    print 'User requires an update'
                    print update_entry
                    print
                    update_list.append(update_entry)

        print
        print 'Update statistics'
        print '%d users require updates' % len(update_list)

        # Get the current data in the filtered file so we can append our new data
        filtered_file = open('filtered.json', 'r')
        filtered_data = json.load(filtered_file)
        filtered_file = open('filtered.json', 'w')

        if filtered_data is None:
            json.dump([], filtered_file)
        else:
            json.dump(filtered_data + update_list, filtered_file)

        # Write the sliced data list to the data file. Removes users that we have processed from the data file.
        data_file = open('data.json', 'w')
        json.dump(data[slice_amount:], data_file)

    @staticmethod
    def get_users():
        """
        Retrieve all users within Qualtrics
        """

        all_users_list = []

        response = util.get_all_qualtrics_users()
        all_users_list.extend(response['result']['elements'])

        next_page = response['result'].get('nextPage', None)
        while next_page:
            response = util.get_all_qualtrics_users(next_page)
            all_users_list.extend(response['result']['elements'])
            next_page = response['result'].get('nextPage', None)
            print next_page

        print 'The length of all the current users is:'
        print len(all_users_list)

        # Create JSON file with the user info
        with open('data.json', 'w+') as outfile:
            json.dump(all_users_list, outfile)

