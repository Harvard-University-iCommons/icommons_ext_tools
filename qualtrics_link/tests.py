from django.test import TestCase
import qualtrics_link.util as util
from icommons_common.models import Person
import datetime
from django.utils import timezone


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

    def test_filter_person_list(self):
        today = timezone.now()
        yesterday = today - datetime.timedelta(days=1)
        # Use tomorrows date for testing, otherwise the microseconds in the today date will be expired by the time used
        tomorrow = today + datetime.timedelta(days=1)

        expired_employee = Person(role_type_cd='employee', role_end_dt=yesterday)
        active_employee = Person(role_type_cd='employee', role_end_dt=tomorrow)
        expired_student = Person(role_type_cd='student', role_end_dt=yesterday)
        active_student = Person(role_type_cd='student', role_end_dt=tomorrow)
        active_employee_none_date = Person(role_type_cd='employee', role_end_dt=None)
        active_student_none_date = Person(role_type_cd='student', role_end_dt=None)
        active_claspart_none_date = Person(role_type_cd='claspart', role_end_dt=None)
        active_claspart = Person(role_type_cd='claspart', role_end_dt=tomorrow)
        expired_claspart = Person(role_type_cd='student', role_end_dt=yesterday)

        self.assertEqual(util.filter_person_list([expired_employee]).role_type_cd, 'employee')
        self.assertEqual(util.filter_person_list([active_employee_none_date]).role_type_cd, 'employee')
        self.assertEqual(util.filter_person_list([active_employee]).role_type_cd, 'employee')

        self.assertEqual(util.filter_person_list([expired_student]).role_type_cd, 'student')
        self.assertEqual(util.filter_person_list([active_student_none_date]).role_type_cd, 'student')
        self.assertEqual(util.filter_person_list([active_student]).role_type_cd, 'student')

        self.assertEqual(util.filter_person_list([expired_employee, active_student]).role_type_cd, 'student')
        self.assertEqual(util.filter_person_list([active_employee, active_student]).role_type_cd, 'employee')
        self.assertEqual(util.filter_person_list([active_employee, expired_student]).role_type_cd, 'employee')
        self.assertEqual(util.filter_person_list([expired_employee, active_student_none_date]).role_type_cd, 'student')
        self.assertEqual(util.filter_person_list([active_employee_none_date, expired_student]).role_type_cd, 'employee')
        self.assertEqual(util.filter_person_list([active_claspart_none_date, expired_claspart]).role_type_cd, 'claspart')
        self.assertEqual(util.filter_person_list([active_claspart, active_student]).role_type_cd, 'student')
        self.assertEqual(util.filter_person_list([expired_employee, active_claspart]).role_type_cd, 'claspart')

        # Do the same tests with the lists reversed
        self.assertEqual(util.filter_person_list([active_student, expired_employee]).role_type_cd, 'student')
        self.assertEqual(util.filter_person_list([active_student, active_employee]).role_type_cd, 'employee')
        self.assertEqual(util.filter_person_list([expired_student, active_employee]).role_type_cd, 'employee')
        self.assertEqual(util.filter_person_list([active_student_none_date, expired_employee]).role_type_cd, 'student')
        self.assertEqual(util.filter_person_list([expired_student, active_employee_none_date]).role_type_cd, 'employee')
