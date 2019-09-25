import logging
import time

from django.core.management.base import BaseCommand

import qualtrics_link.util as util
from icommons_common.models import Person
from qualtrics_link.models import QualtricsUser

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        qualtrics_user_univ_ids = list(QualtricsUser.objects.filter(last_login__gte='2018-09-25 12:00:00+00').values_list('univ_id', flat=True))

        spacer = '          '
        complete_match_count = 0
        only_division_match_count = 0
        only_role_match_count = 0
        both_values_mismatch_count = 0

        div_changes = {}
        role_changes = {}
        no_iam_details = []  # List to contain the HUID'S of failed lookups in the new IAM view
        expired_users = []  # Users who have an expired role end date

        start_time = time.time()

        i = 1
        q_id_len = len(qualtrics_user_univ_ids)
        for q_id in qualtrics_user_univ_ids:

            try:
                person_iam = util.get_person_details(q_id)
            except Person.DoesNotExist:
                print 'No Person details for {}'.format(q_id)
                continue

            if person_iam:
                print 'Comparing info for {}   ({} out of {})'.format(person_iam.id, i, q_id_len)
                person = QualtricsUser.objects.filter(univ_id=person_iam.id).order_by('-last_login')[0]
                matched_division = True
                matched_role = True
                if person_iam.division != person.division:
                    print spacer + 'No match division IAM: {} LPP: {} {}'.format(person_iam.division, person.division, person_iam.id)
                    matched_division = False

                    try:
                        # Track the change in division from old to new
                        div = div_changes[person.division]
                        try:
                            div[person_iam.division] += 1
                        except KeyError:
                            div[person_iam.division] = 1
                    except KeyError:
                        div_changes[person.division] = {person_iam.division: 1}

                if person_iam.role.lower() != person.user_type.lower():
                    print spacer + 'No role match IAM: {} LPP: {} {}'.format(person_iam.role.lower(), person.user_type.lower(), person_iam.id)
                    matched_role = False

                    try:
                        # Track the change in division from old to new
                        role = role_changes[person.user_type]
                        try:
                            role[person_iam.role.lower()] += 1
                        except KeyError:
                            role[person_iam.role.lower()] = 1
                    except KeyError:
                        role_changes[person.user_type] = {person_iam.role.lower(): 1}

                if matched_division and matched_role:
                    complete_match_count += 1
                elif matched_role and not matched_division:
                    only_role_match_count += 1
                elif matched_division and not matched_role:
                    only_division_match_count += 1
                else:
                    both_values_mismatch_count += 1
            else:
                expired_users.append(q_id)
        # except Exception as e:
        #     print "EXCEPTION! {}".format(e.message)
        #     i += 1

        elapsed_time = time.time() - start_time
        print elapsed_time

        print
        print 'Complete match count: {}'.format(complete_match_count)
        print 'Only role mismatch: {}'.format(only_division_match_count)
        print 'Only division mismatch: {}'.format(only_role_match_count)
        print 'Both dont match count: {}'.format(both_values_mismatch_count)
        print 'Expired users: {}'.format(len(expired_users))
        print 'Total users: {}'.format(len(qualtrics_user_univ_ids))
        print
        print div_changes
        print
        print role_changes
        print
        print 'No IAM Details'
        print no_iam_details
        print
        print 'Expired user HUIDs'
        print expired_users
