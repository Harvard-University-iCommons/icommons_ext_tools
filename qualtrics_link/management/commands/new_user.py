from django.core.management.base import BaseCommand
from qualtrics_link import util
import datetime
import time
import requests


class Command(BaseCommand):

    def handle(self, *args, **options):
        print 'Creating user'
        current_time = time.time()
        current_date = datetime.datetime.utcfromtimestamp(current_time).strftime('%Y-%m-%dT%H:%M:%S')

        # Get the expiration date in the correct format i.e. '2008-07-16T15:42:51' (date format is same as above)
        # In this case we take the current time and add 5 minutes (300 seconds)
        expiration_date = datetime.datetime.utcfromtimestamp(current_time + 300).strftime('%Y-%m-%dT%H:%M:%S')

        # Change the huid string by decreasing by 1 on each run of this command
        enc_id = util.get_encrypted_huid('99999992')
        key_value_pairs = u"id={}&timestamp={}&expiration={}&firstname={}&lastname={}&email={}&UserType={}&Division={}"
        key_value_pairs = key_value_pairs.format(enc_id,
                                                 current_date,
                                                 expiration_date,
                                                 'Chris',
                                                 'Thornton',
                                                 'chris6@test.com',
                                                 'employee',
                                                 util.DIVISION_MAPPING['FAS'])
        qualtrics_link = util.get_qualtrics_url(key_value_pairs)

        req = requests.get(qualtrics_link)

        print req
        print 'Sent request'
