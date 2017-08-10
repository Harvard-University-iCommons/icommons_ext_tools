from django.test import TestCase
import qualtrics_link.util as util


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

    def test_lookup_school_affiliations(self):
        # Test valid lookup
        self.assertEqual(util.lookup_school_affiliations(39), 'DIV')

        # Test empty employee school code
        self.assertEqual(util.lookup_school_affiliations(92), '')

        # Test invalid school code
        self.assertEqual(util.lookup_school_affiliations(9999), 'Not Available')
