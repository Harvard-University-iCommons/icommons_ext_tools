

'''
For some of the tests below, I am setting the __doc__ attribute for each method to be the message that is appended 
to the assertion in the event the assertion failed. This takes the form self.method.__doc__
'''

import unittest
import mock
from mock import patch
from .views import CourseIndexView
from django.core.urlresolvers import resolve
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin
from django.test import RequestFactory
from icommons_common.models import CourseInstance


class CourseIndexViewTest(unittest.TestCase):
    longMessage = True

    def setUp(self):
        view = CourseIndexView()
        view.request = RequestFactory().get('/fake-path')
        view.request.session = {}  # Default session to empty dict
        # Object is populated by the DetailView parent class by primary key during dispatch
        view.object = CourseInstance(course_instance_id=9999)
        self.view = view

    def test_resolve_route_to_view(self):
        match = resolve('/courses/123/', 'canvas_course_wizard.urls')
        self.assertEqual(match.view_name, 'course-index',
                         "named-url for course index didn't match expected result")
        self.assertEqual('CourseIndexView', match.func.__name__)
        self.assertEqual(len(match.args), 0, 'Should be no args for course wizard index view')
        self.assertEqual(len(match.kwargs), 1, 'Should be one keyword argument for course index')
        self.assertEqual(match.kwargs['pk'], '123',
                         'Keyword argument \'pk\' should match end of url')

    def test_view_instance_setup(self):
        self.assertIsInstance(self.view, DetailView,
                              'Course index view expected to be a subclass of DetailView')
        self.assertIsInstance(self.view, LoginRequiredMixin,
                              'Course index view expected to be a subclass of LoginRequiredMixin')
        self.assertEquals(self.view.template_name, 'canvas_course_wizard/course.html',
                          'Template for course index does not match expected value')
        self.assertIs(self.view.model, CourseInstance, 'Model lookup type should be CourseInstance')
        self.assertEqual(self.view.context_object_name, 'course',
                         "context should reference the course instance as 'course'")

    # is_current_user_member_of_course_staff tests

    '''
    This test is mainly to make sure that default value is provided for session call so that a dict
    key exception is not raised
    '''

    def test_is_current_user_member_of_course_staff_when_no_user_groups_in_session(self):
        course_instance_id = self.view.object.course_instance_id
        response = self.view.is_current_user_member_of_course_staff(course_instance_id)
        self.assertEquals(response, False,
                          'User with no groups defined in session should return False')

    def test_is_current_user_member_of_course_staff_when_user_member_of_no_groups(self):
        course_instance_id = self.view.object.course_instance_id
        self.view.request.session = {'USER_GROUPS': []}
        response = self.view.is_current_user_member_of_course_staff(course_instance_id)
        self.assertEquals(response, False, 'User with no groups should result return False')

    def test_is_current_user_member_of_course_staff_when_user_member_of_non_staff_course_group(self):
        course_instance_id = self.view.object.course_instance_id
        self.view.request.session = {'USER_GROUPS': ['ScaleCourseStudent:%d' % course_instance_id]}
        response = self.view.is_current_user_member_of_course_staff(course_instance_id)
        self.assertEquals(response, False, 'Non-teaching staff should result return False')

    def test_is_current_user_member_of_course_staff_when_user_member_of_another_course_staff(self):
        course_instance_id = self.view.object.course_instance_id
        self.view.request.session = {'USER_GROUPS':
                                     ['ScaleCourseStaff:%d' % (course_instance_id - 1)]}
        response = self.view.is_current_user_member_of_course_staff(course_instance_id)
        self.assertEquals(response, False,
                          'Teaching staff for a different course should return False')

    def test_is_current_user_member_of_course_staff_when_user_member_of_course_staff(self):
        course_instance_id = self.view.object.course_instance_id
        self.view.request.session = {'USER_GROUPS': ['ScaleCourseStaff:%d' % course_instance_id]}
        response = self.view.is_current_user_member_of_course_staff(course_instance_id)
        self.assertEquals(response, True, 'Teaching staff for course should return True')

    # get_urls_from_course_instance_id

    def create_mock_list_multi(self):
        '''
        Create and populate a mock list with isite and canvas data
        '''
        mock_list = mock.MagicMock(name='mock_list')
        mock_item_one = mock.Mock(name='mock_item_one')
        mock_item_two = mock.Mock(name='mock_item_two')
        mock_item_three = mock.Mock(name='mock_item_three')
        mock_item_one.course_site.external_id = 'k12345'
        mock_item_one.course_site.site_type_id = 'isite'
        mock_item_two.course_site.external_id = 'k12346'
        mock_item_two.course_site.site_type_id = 'isite'
        mock_item_three.course_site.external_id = 'https://canvas.harvard.edu/courses/456'
        mock_item_three.course_site.site_type_id = 'external'
        mock_list.__iter__.return_value = [mock_item_one, mock_item_two, mock_item_three]

        return mock_list

    def create_mock_list_single_isite(self):
        '''
        Create and populate a mock list with isite data
        '''
        mock_list = mock.MagicMock(name='mock_list')
        mock_item_one = mock.Mock(name='mock_item_one')
        mock_item_one.course_site.external_id = 'k12345'
        mock_item_one.course_site.site_type_id = 'isite'
        mock_list.__iter__.return_value = [mock_item_one]

        return mock_list

    def create_mock_list_single_canvas(self):
        '''
        Create and populate a mock list with isite and canvas data
        '''
        mock_list = mock.MagicMock(name='mock_list')
        mock_item_one = mock.Mock(name='mock_item_one')
        mock_item_one.course_site.external_id = 'https://canvas.harvard.edu/courses/456'
        mock_item_one.course_site.site_type_id = 'external'
        mock_list.__iter__.return_value = [mock_item_one]

        return mock_list

    def create_mock_list_empty(self):
        '''
        Create and init an empty mock list
        '''
        mock_list = mock.MagicMock(name='mock_list')
        mock_list.__iter__.return_value = []

        return mock_list

    @patch.dict('canvas_course_wizard.views.settings.COURSE_WIZARD', {'OLD_LMS_URL': 'http://isites.harvard.edu/'})
    @patch("canvas_course_wizard.views.SiteMap.objects.filter")
    def test_get_urls_from_course_instance_id_call_to_site_map(self, mock_sitemap):
        '''
        test the method get_urls_from_course_instance_id by setting the mock_sitemap query to return a list of data
        '''
        course_instance_id = self.view.object.course_instance_id
        self.view.get_urls_from_course_instance_id(course_instance_id)

        mock_sitemap.assert_called_once_with(
            course_instance__course_instance_id=course_instance_id, map_type__map_type_id='official')

    @patch.dict('canvas_course_wizard.views.settings.COURSE_WIZARD', {'OLD_LMS_URL': 'http://isites.harvard.edu/'})
    @patch("canvas_course_wizard.views.SiteMap.objects.filter")
    def test_get_urls_from_course_instance_id_multiple(self, mock_sitemap):
        '''
        test the method get_urls_from_course_instance_id by setting the mock_sitemap query to return a list of data
        '''
        mock_sitemap.return_value = self.create_mock_list_multi()
        data = self.view.get_urls_from_course_instance_id(0)

        test_data = ['http://isites.harvard.edu/k12345',
                     'http://isites.harvard.edu/k12346',
                     'https://canvas.harvard.edu/courses/456']

        self.assertEquals(
            data,
            test_data,
            self.test_get_urls_from_course_instance_id_multiple.__doc__)

    @patch.dict('canvas_course_wizard.views.settings.COURSE_WIZARD', {'OLD_LMS_URL': 'http://isites.harvard.edu/'})
    @patch("canvas_course_wizard.views.SiteMap.objects.filter")
    def test_get_urls_from_course_instance_id_empty(self, mock_sitemap):
        '''
        test the method get_urls_from_course_instance_id by setting the mock_sitemap query to return an empty list
        '''
        mock_sitemap.return_value = self.create_mock_list_empty()
        data = self.view.get_urls_from_course_instance_id(0)

        self.assertEquals(
            data, [],
            self.test_get_urls_from_course_instance_id_empty.__doc__)

    '''
    Expectation entering the get_context_data is that the object has been found... a 404 error would have been
    raised before getting to this method, so we'll do the minimal setup required
    '''

    # @patch("canvas_course_wizard.views.SiteMap.objects.filter")
    # @patch("canvas_course_wizard.views.super", create=True)
    # def test_get_context_data_for_non_canvas_course_as_teaching_staff(self, mock_super, mock_sitemap):

    #     # Make sure user is considered a staff member
    #     mock_is_staffer = mock.Mock(name='is_staffer', return_value=True)
    #     # Course instance to use for test
    #     mock_ci = CourseInstance(course_instance_id=9999)

    #     view = CourseIndexView()
    #     view.request = self.request
    #     view.object = mock_ci
    #     view.is_current_user_member_of_course_staff = mock_is_staffer

    #     with mock.patch('canvas_course_wizard.views.super', create=True) as mock_super:
    #         # Set up the patch mocks
    #         mock_super.return_value.get_context_data.return_value = {}
    #         # Make the call
    #         context = view.get_context_data()

    #     mock_is_staffer.assert_called_once_with(mock_ci.course_instance_id)
    #     self.assertTrue(context['show_create'],
    #                     'A teaching staffer for a non-canvas course should be able to create')

    # def setup_view_with_staffer(self, mock_is_staffer):
    #     '''
    #     Help method used to setup the view for tests
    #     '''
    #     view = self.setup_view()
    #     view.is_current_user_member_of_course_staff = mock_is_staffer

    #     return view

    # @patch("canvas_course_wizard.views.SiteMap.objects.filter")
    # @patch("canvas_course_wizard.views.super", create=True)
    # def test_case_where_there_are_multiple_isites_returned(self, mock_super, mock_sitemap):
    #     '''
    #     Given a course instance_id that has an isite setup, the url to the isite should be 
    #     constructed and returned in the context
    #     '''

    #     # Make sure user is considered a staff member
    #     mock_is_staffer = mock.Mock(name='is_staffer', return_value=True)

    #     # Course instance to use for test
    #     #mock_ci = CourseInstance(course_instance_id=9999)
    #     view = self.setup_view_with_staffer(mock_is_staffer)
    #     mock_sitemap.return_value = self.create_mock_list_multi()
    #     mock_super.return_value.get_context_data.return_value = {}

    #     view.get_urls_from_course_instance_id = mock.Mock()

    #     # Make the call to get_context_date
    #     context = view.get_context_data()

    #     # test to see if the mock was called once with the data 9999
    #     view.get_urls_from_course_instance_id.assert_called_once_with(9999)

    # @patch("canvas_course_wizard.views.SiteMap.objects.filter")
    # @patch("canvas_course_wizard.views.super", create=True)
    # def test_case_where_the_list_is_empty(self, mock_super, mock_sitemap):
    #     '''
    #     Given a course instance_id that does not have any isites, isite_course_url
    #     should be an empty list
    #     '''

    #     mock_is_staffer = mock.Mock(name='is_staffer', return_value=True)
    #     #mock_ci = CourseInstance(course_instance_id=9999)
    #     view = self.setup_view_with_staffer(mock_is_staffer)
    #     mock_sitemap.return_value = self.create_mock_list_empty()
    #     mock_super.return_value.get_context_data.return_value = {}

    #     # Make the call to get_context_date
    #     context = view.get_context_data()

    #     # test that the lists match
    #     self.assertEquals(
    #         context['lms_course_urls'], [],
    #         self.test_case_where_the_list_is_empty.__doc__)
