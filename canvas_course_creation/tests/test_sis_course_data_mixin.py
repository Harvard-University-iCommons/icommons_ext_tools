from mock import Mock, MagicMock, patch
from unittest import TestCase
from canvas_course_creation.models import SISCourseDataMixin


class SISCourseDataStub(SISCourseDataMixin):
    """ An implementation of the course data mixin used for testing """
    course = MagicMock(registrar_code='FAS1234', school_id='fas')
    term = MagicMock()
    sub_title = None


class SISCourseDataMixinTest(TestCase):

    def setUp(self):
        self.course_data = SISCourseDataStub()

    def test_sis_term_id_returns_string(self):
        """ Test that result of sis_term_id property is string result of meta_term_id call """
        term_id = 'formatted term id string'
        self.course_data.term.meta_term_id.return_value = term_id
        result = self.course_data.sis_term_id
        self.assertEqual(result, term_id)

    def test_sis_term_id_returns_none(self):
        """ Test that result of sis_term_id property is none result of meta_term_id call """
        self.course_data.term.meta_term_id.return_value = None
        result = self.course_data.sis_term_id
        self.assertEqual(result, None)

    def test_sis_account_id_returns_course_group_key_if_course_groups(self):
        """
        Test that result of sis_account_id is formatted primary key of first course group
        when there is at least one associated course group.
        """
        course_group_pk = 12345
        self.course_data.course.course_groups.count.return_value = 1
        self.course_data.course.course_groups.first.return_value = Mock(pk=course_group_pk)
        result = self.course_data.sis_account_id
        self.assertEqual(result, 'coursegroup:%s' % course_group_pk)

    def test_sis_account_id_returns_course_group_key_if_course_groups_and_departments(self):
        """
        Test that result of sis_account_id is formatted primary key of first course group
        when there is at least one associated course group, as well as departments.
        """
        course_group_pk = 12345
        self.course_data.course.course_groups.count.return_value = 1
        self.course_data.course.departments.count.return_value = 1
        self.course_data.course.course_groups.first.return_value = Mock(pk=course_group_pk)
        result = self.course_data.sis_account_id
        self.assertEqual(result, 'coursegroup:%s' % course_group_pk)

    def test_sis_account_id_returns_department_key_if_departments_and_no_course_groups(self):
        """
        Test that result of sis_account_id is formatted primary key of first department
        when there is at least one associated departments, but no course groups.
        """
        department_pk = 54321
        self.course_data.course.course_groups.count.return_value = 0
        self.course_data.course.departments.count.return_value = 1
        self.course_data.course.departments.first.return_value = Mock(pk=department_pk)
        result = self.course_data.sis_account_id
        self.assertEqual(result, 'dept:%s' % department_pk)

    def test_sis_account_id_returns_school_key_if_no_departments_and_no_course_groups(self):
        """
        Test that result of sis_account_id is formatted pk of associated school if there are
        no associated departments and no course groups.
        """
        school_id = self.course_data.course.school_id
        self.course_data.course.course_groups.count.return_value = 0
        self.course_data.course.departments.count.return_value = 0
        result = self.course_data.sis_account_id
        self.assertEqual(result, 'school:%s' % school_id)

    def test_course_code_returns_short_title_if_exists(self):
        """ Test that result of the course code is the short_title field of the course data object """
        short_title = 'A short course title'
        self.course_data.short_title = short_title
        result = self.course_data.course_code
        self.assertEqual(result, short_title)

    def test_course_code_returns_short_title_if_exists_and_registrar_code_display_exists(self):
        """
        Test that result of the course code is the short_title field of the course data object even
        if the associated course has a registrar_code_display field.
        """
        short_title = 'A short course title'
        self.course_data.short_title = short_title
        self.course_data.course.registrar_code_display = 'a display code'
        result = self.course_data.course_code
        self.assertEqual(result, short_title)

    def test_course_code_returns_registrar_code_display_if_exists_and_no_short_title(self):
        """
        Test that result of the course code is the registrar_code_display field of the associated course
        if the course data object does not have a short_title.
        """
        registrar_code_display = 'display-code-for-registrar'
        self.course_data.course.registrar_code_display = registrar_code_display
        self.course_data.short_title = None
        result = self.course_data.course_code
        self.assertEqual(result, registrar_code_display)

    def test_course_code_returns_registrar_code_if_no_short_title_and_no_registrar_display_code(self):
        """
        Test that result of the course code is the registrar_code field of the associated course if
        the course data object does not have a short_title and the course does not have a
        registrar_code_display field.
        """
        registrar_code = 'registrar-code'
        self.course_data.course.registrar_code_display = None
        self.course_data.short_title = None
        self.course_data.course.registrar_code = registrar_code
        result = self.course_data.course_code
        self.assertEqual(result, registrar_code)

    def test_course_name_returns_title_if_exists(self):
        """ Test that result of the course_name property is the course data object title. """
        title = 'course title'
        self.course_data.title = title
        result = self.course_data.course_name
        self.assertEqual(result, title)

    def test_course_name_returns_course_code_if_no_title(self):
        """ Test that result of the course_name property is the course_code property if no title exists. """
        self.course_data.title = None
        course_code = 'a sample course code'
        with patch.object(SISCourseDataStub, 'course_code', course_code):
            result = self.course_data.course_name
        self.assertEqual(result, course_code)

    def test_course_name_appends_sub_title_to_title_if_exists(self):
        """ Test that a subtitle is appended to an existing title if exists. """
        title = 'course title'
        sub_title = 'course sub_title'
        self.course_data.title = title
        self.course_data.sub_title = sub_title
        result = self.course_data.course_name
        self.assertEqual(result, '%s: %s' % (title, sub_title))

    def test_course_name_appends_sub_title_to_course_code_if_exists(self):
        """ Test that a subtitle is appended to the course_code if exists and no title exists. """
        self.course_data.title = None
        sub_title = 'course sub_title'
        self.course_data.sub_title = sub_title
        course_code = 'a sample course code'
        with patch.object(SISCourseDataStub, 'course_code', course_code):
            result = self.course_data.course_name
        self.assertEqual(result, '%s: %s' % (course_code, sub_title))

    def test_primary_section_name_formats_school_id_and_course_code(self):
        """
        Test that the primary section name is a formatted string based on school id and
        course_code properties.
        """
        course_code = 'a sample course code'
        school_id = self.course_data.course.school_id
        with patch.object(SISCourseDataStub, 'course_code', course_code):
            result = self.course_data.primary_section_name()
        self.assertEqual(result, '%s %s' % (school_id.upper(), course_code))
