import json
import logging

from django.core.management.base import BaseCommand

from icommons_common.models import Person
from qualtrics_link import util

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'This command works in three steps; ' \
           '1. Get all Qualtrics users; ' \
           '2. Find those that need to be updated;' \
           '3. Update the users from step 2 via the Qualtrics API.'

    def add_arguments(self, parser):
        parser.add_argument('--get-users', action='store_true', help='Query Qualtrics to get all users and store them '
                                                                     'in a data.json file.')
        parser.add_argument('--filter-users', action='store_true', help='Filters the data.json file to produce a new'
                                                                        'file containing only users that need to be '
                                                                        'updated.')
        parser.add_argument('--perform-update', action='store_true', help='Perform the update of Qualtrics user using '
                                                                          'the filtered list file.')
        parser.add_argument('--stats', action='store_true', help='Provide information regarding the changes that are '
                                                                 'to be made during an update.')
        parser.add_argument('--update-stats', action='store_true', help='Provide information from the '
                                                                        'perform-update call')
        parser.add_argument('--amount', default=50, type=int, help='The amount of users to filter in a run.')

    def handle(self, *args, **options):
        if options['get_users']:
            self.get_users()
        if options['filter_users']:
            self.filter_users(options['amount'])
        elif options['stats']:
            self.stats()
        elif options['perform_update']:
            self.update_users()
        elif options['update_stats']:
            self.update_stats()
        else:
            logger.info('You need to select a valid option')

    @staticmethod
    def update_stats():
        """
        Prints the information from the update run to console
        """
        try:
            update_stats_file = open('update_stats.json', 'r')
            update_data = json.load(update_stats_file)

            logger.info('The following accounts failed to update:')
            logger.info('\n')
            for detail in update_data['failure_details']:
                logger.info('Qualtrics ID: %s, HUID: %s' % (detail['user']['user_id'],
                                                            detail['user']['changes']['user']['huid']))

                logger.info('HTTP Status: %s' % detail['response']['meta']['httpStatus'])
                logger.info('Error Code: %s' % detail['response']['meta']['error']['errorCode'])
                logger.info('Error Message: %s' % detail['response']['meta']['error']['errorMessage'])

                logger.info('Role changing from %s => %s' % (detail['user']['changes']['previous_data']['role'],
                                                             detail['user']['changes']['new_data']['role']))
                logger.info('Division changing from %s => %s' % (detail['user']['changes']['previous_data']['division'],
                                                                 detail['user']['changes']['new_data']['division']))
                logger.info('\n')

            logger.info('Total users requiring an update: %d' % update_data['total'])
            logger.info('Total failures: %d' % update_data['failure'])
            logger.info('Total successes: %d' % update_data['success'])
        except IOError:
            logger.info('There is no update information currently available')

    @staticmethod
    def stats():
        filtered_file = open('filtered.json', 'r')
        filtered_data = json.load(filtered_file)

        logger.info('------------------------------------------------------------')

        # Display information regarding the users who will have their account updated
        for update in filtered_data:
            logger.info('User %s %s with HUID: %s has the following update:' % (update['changes']['user']['first_name'],
                                                                                update['changes']['user']['last_name'],
                                                                                update['changes']['user']['huid']))
            logger.info('Role is changing from %s => %s' % (update['changes']['previous_data']['role'],
                                                            update['changes']['new_data']['role']))
            logger.info('Division is changing from %s => %s' % (update['changes']['previous_data']['division'],
                                                                update['changes']['new_data']['division']))
            logger.info('------------------------------------------------------------')
        logger.info('Total amount of users being updated: %d' % len(filtered_data))

    @staticmethod
    def update_users():
        """
        Will go through the list of users in the filtered file and update the users information via the Qualtrics API.
        """
        filtered_file = open('filtered.json', 'r')
        filtered_data = json.load(filtered_file)
        filtered_len = len(filtered_data)

        stats_file = open('update_stats.json', 'w')

        stats = {
            'total': filtered_len,
            'success': 0,
            'failure': 0,
            'failure_details': []  # List of user and response dicts detailing the failure
        }

        count = 1
        for user in filtered_data:
            logger.info('Updating %d of %d records' % (count, filtered_len))
            resp = util.update_qualtrics_user(user_id=user['user_id'],
                                              division=user['division'],
                                              role=user['role']).json()
            if resp['meta']['httpStatus'] != '200 - OK':
                logger.warning('Response returned a status other than 200')
                logger.warning('Response: %s' % resp)
                stats['failure'] += 1
                stats['failure_details'].append({'user': user,
                                                 'response': resp})
            else:
                stats['success'] += 1

            count += 1

        # Writes the updated stats dict to file
        json.dump(stats, stats_file)

        logger.info('Update complete')
        logger.info(stats)

    @staticmethod
    def filter_users(slice_amount):
        """
        Go through all the Qualtrics users in the data file and find those who do not match our current People data.
        Create a new filtered file containing those users who will be updated in another step.
        """
        employee_user_type = 'UT_egutew4nqz71QgI'
        student_user_type = 'UT_787UadC574xhxgU'
        brand_admin = 'UT_BRANDADMIN'
        user_type_list = [employee_user_type, student_user_type, brand_admin]

        user_type_mapping = {
            'employee': 'UT_egutew4nqz71QgI',
            'student': 'UT_787UadC574xhxgU',
            'brand administrator': 'UT_BRANDADMIN'
        }

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

        #####
        # This section contains reverse lookups based on Qualtrics specific ID's
        # This is used to create a readable format when outputting to console.
        #####

        reverse_user_types = {
            'UT_egutew4nqz71QgI': 'Employee',
            'UT_787UadC574xhxgU': 'Student',
            'UT_BRANDADMIN': 'Brand Admin',
            'UT_8vKYJklycpVKpiA': 'Generic',
            'UT_4TQJ8h7ffJklndG': 'XID',
            'UT_3dBUKOs5wAT2mLW': 'Standard Qualtrics',
            'UT_4SjjZmbPphZGKDq': 'Standard - Qualtrics - no limits',
            'UT_5hIxADmZZF1O2jy': 'Full Trial',
            'UT_cAchjVb6asRttat': 'QTrial Default 102015',
            'UT_eJQs8UTd28L5L25': 'QTrial Academic',
            'UT_SELFENROLLMENT': 'Default Self-Enrollment Type'
        }

        # Reverse mapping to translate the Qualtrics division code into a readable division
        reverse_division_mapping = {
            'DV_0uG93Am70qIFb00': 'FAS',
            'DV_eesMPIncvHA270U': 'GSE',
            'DV_cvfNy3UwERh9IcA': 'HSPH',
            'DV_1zu8x43ZIyqzWlu': 'Other',
            'DV_bdu3uP2WTYThpOY': 'HKS',
            'DV_cSx7CCmUZ1DaS3i': 'EXT',
            'DV_6DN9Q7jTRzsxgHy': 'HLS',
            'DV_77MUQ7NsyaGcQU4': 'HUIT',
            'DV_7V89XC1uxWU2ODW': 'GSD',
            'DV_6Fhm425s7ozZM5D': 'Central Administration',
            'DV_5o8WAy3WJXLNX2Q': 'HDS',
            'DV_1WSu6zRMeNx6ZYU': 'HAA (Alumni Assoc.)',
            'DV_8dpaRpPHqefdNAx': 'VPAL Research and Affiliates',
            'DV_1Ro0atRhq0UV9ti': 'Berkman',
            'DV_agzgkeDIaZPEJHD': 'Radcliffe',
            'DV_23NVy6XjBHhOXxX': 'API Div',
            'DV_0vsxWeIjXJWeS21': 'GSE-PPE [no longer used]',
            'None': 'None'
        }
        #####

        data_file = open('data.json', 'r')
        data = json.load(data_file)
        logger.info(('%d records in file' % len(data)))

        # List of all users that need to be updated
        update_list = []

        position = 1
        for q_person in data[:slice_amount]:
            logger.info('Processing user %d out of %d' % (position, slice_amount))
            q_id = q_person['id']
            q_username = q_person['username']
            q_division = q_person['divisionId']
            q_role = q_person['userType']
            q_email = q_person['email']
            q_first_name = q_person['firstName']
            q_last_name = q_person['lastName']

            # Filter Person records based off of their email if present
            if q_email:
                person_queryset = Person.objects.filter(email_address=q_email)
                # A user may have had their Qualtrics account created with a different email address than what
                # is currently stored in our DB. If so, we need to look them up based on first and last name.
                if len(person_queryset) == 0:
                    person_queryset = Person.objects.filter(name_first=q_first_name, name_last=q_last_name)
            else:
                person_queryset = Person.objects.filter(name_first=q_first_name, name_last=q_last_name)

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
                p_role = user_type_mapping[person_details.role]
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

                # If the Person is not a Student or Employee, or Brand Admin then they need to be updated
                # Or if their roles do not match
                if q_role not in user_type_list or p_role != q_role:
                    update_dict['user_type'] = p_role
                    update_person = True

                # If the update person bool has been set to True, then get the values from the update dict to be
                # added to the update list.
                if update_person:
                    # If the only update is the users division and they are a brand admin, the role will default to the
                    # persons role of Employee. If they are a brand admin in Qualtrics, set their role to stay the same
                    # in the default case.
                    if q_role == brand_admin:
                        p_role = brand_admin

                    # Use the Person record value as a default in the case of only one field needing to be updated.
                    update_entry = {
                        'user_id': update_dict.get('user_id'),
                        'division': update_dict.get('division', p_division),
                        'role': update_dict.get('role', p_role),
                    }

                    # Have a readable/translated changes portion or the entry that can be output to console to show what
                    # has changed
                    if q_division is None:
                        q_division = 'None'

                    update_entry['changes'] = {
                        'user': {
                            'huid': person_details.id,
                            'first_name': person_details.first_name,
                            'last_name': person_details.last_name
                        },
                        'previous_data': {
                            'division': reverse_division_mapping[q_division],
                            'role': reverse_user_types[q_role]
                        },
                        'new_data': {
                            'division': reverse_division_mapping[update_entry['division']],
                            'role': reverse_user_types[update_entry['role']]
                        }
                    }

                    logger.info('Found user requiring update, Qualtrics ID: %s, HUID: %s' % (q_id, person_details.id))
                    update_list.append(update_entry)
            else:
                logger.info('Could not find matching person in DB; Qualtrics id:%s' % q_id)

            position += 1

        logger.info('\n')
        logger.info('Update statistics')
        logger.info('%d users require updates' % len(update_list))

        # Get the current data in the filtered file so we can append our new data
        filtered_file = open('filtered.json', 'r')
        filtered_data = json.load(filtered_file)
        filtered_file = open('filtered.json', 'w')
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
            logger.info(next_page)

        logger.info('All user count: %d' % len(all_users_list))

        # Create JSON file with the user info
        with open('data.json', 'w+') as outfile:
            json.dump(all_users_list, outfile)

        # Create a clean instance of the filtered and stats files
        filtered_file = open('filtered.json', 'w')
        json.dump([], filtered_file)
        open('update_stats.json', 'w')
