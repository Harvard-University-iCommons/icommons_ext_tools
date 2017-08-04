from django.test import TestCase
import qualtrics_link.util as util
from unittest import skip


class UtilTestCase(TestCase):

    def test_lookup_unit(self):
        self.assertEqual(util.lookup_unit('FAS'), 'FAS')
        self.assertEqual(util.lookup_unit('DOES_NOT_EXIST'), 'Other')

    def test_is_unit_valid(self):
        self.assertTrue(util.is_unit_valid('HUIT'))
        self.assertFalse(util.is_unit_valid('HBS'))
        self.assertFalse(util.is_unit_valid('HMS'))
        self.assertFalse(util.is_unit_valid('HSDM'))
        self.assertFalse(util.is_unit_valid('HBP'))

    def test_get_valid_school(self):
        # User with multiple school affiliations, blacklist first
        schools_blacklist_first = ['HMS', 'SUM', 'KSG']
        self.assertEqual(util.get_valid_school(schools_blacklist_first), 'EXT')
        # User with one school affiliation
        schools_blacklist_first = ['KSG']
        self.assertEqual(util.get_valid_school(schools_blacklist_first), 'HKS')
        # User with no school affiliations
        self.assertIsNone(util.get_valid_school([]))

    def test_get_valid_dept(self):
        self.assertEqual(util.get_valid_dept('MAG'), 'Central Administration',)
        self.assertEqual(util.get_valid_dept('NO_AREA'), 'Other')
        self.assertEqual(util.get_valid_dept(None), 'Other')
        self.assertIsNone(util.get_valid_dept('HMS'))

    @skip("Skipping until changes are made in view and util")
    def test_build_user_dict(self):
        people_in_data = {
            'people': [
                {
                    'first_name': 'firstName',
                    'last_name': 'lastName',
                    'schoolAfilliations': [],
                    'departmentAffiliation': 'UIS'
                },
            ]
        }
        return_dict = {
            'first_name': 'firstName',
            'last_name': 'lastName',
            'division': 'HUIT',
            'role': 'employee',
            'validschool': False,
            'validdept': True,
        }
        pass
        self.assertEqual(util.build_user_dict(people_in_data), return_dict)
