import datetime
import logging
import random
import time

from django.core.management.base import BaseCommand
from faker import Faker
from qualtrics_link import util

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = """
        This command generates a Qualtrics authentication token for fake data.
    """

    def handle(self, *args, **options):

        # make up a fake HUID
        fake_huid = 'fake{}'.format(random.randint(1000, 9999))
        enc_id = util.get_encrypted_huid(fake_huid)

        current_time = time.time()
        current_date = datetime.datetime.utcfromtimestamp(current_time).strftime('%Y-%m-%dT%H:%M:%S')
        # for this test token, make the expiration one day in the future
        expiration_date = datetime.datetime.utcfromtimestamp(current_time + 86400).strftime('%Y-%m-%dT%H:%M:%S')

        fake = Faker()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = '{}.{}@fake.harvard.edu'.format(first_name.lower(), last_name.lower())

        # UserType is either employee or student
        user_type = random.choice(['student', 'employee'])

        # Division
        div_name, div_id = random.choice(list(util.DIVISION_MAPPING.items()))

        key_value_pairs = "id={}&timestamp={}&expiration={}&firstname={}&lastname={}&email={}&UserType={}&Division={}".format(
            enc_id, current_date, expiration_date, first_name, last_name, email, user_type, div_id
        )

        login_url = util.get_qualtrics_url(key_value_pairs)

        print(('{}: {}\n{} {}, {}, {}, {}\n{}\n{}'.format(fake_huid, enc_id,
            first_name, last_name, email, user_type, div_name, key_value_pairs, login_url)))
