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

    @patch.object(CourseIndexView, 'get_urls_from_course_instance_id')
    @patch.object(CourseIndexView, 'is_current_user_member_of_course_staff')
    @patch("canvas_course_wizard.views.super", create=True)
    def test_get_context_data_calls_helper_methods(self, mock_super, mock_staffer, mock_course_urls):
        course_object = self.view.object

        self.view.get_context_data()

        mock_super.assert_called_any()
        mock_staffer.assert_called_once_with(course_object.course_instance_id)
        mock_course_urls.assert_called_once_with(course_object.course_instance_id)

    @patch.object(CourseIndexView, 'get_urls_from_course_instance_id')
    @patch.object(CourseIndexView, 'is_current_user_member_of_course_staff')
    @patch("canvas_course_wizard.views.super", create=True)
    def test_get_context_data_returns_course_site_urls_context(self, mock_super, mock_staffer, mock_course_urls):
        mock_super.return_value.get_context_data.return_value = {}
        context = self.view.get_context_data()

        self.assertEquals(context['lms_course_urls'], mock_course_urls.return_value,
                          "Value of course_site_url context variable should be return value of call to get_urls_from_course_instance_id")

    @patch.object(CourseIndexView, 'get_urls_from_course_instance_id', return_value=None)
    @patch.object(CourseIndexView, 'is_current_user_member_of_course_staff', return_value=False)
    @patch("canvas_course_wizard.views.super", create=True)
    def test_get_context_data_course_creation_as_non_staff_with_no_course_sites(self, mock_super, mock_staffer, mock_course_urls):
        mock_super.return_value.get_context_data.return_value = {}
        context = self.view.get_context_data()
        self.assertEquals(context['user_can_create_course'], False,
                          'User should not be able to create course if they are not a staff member')

    @patch.object(CourseIndexView, 'get_urls_from_course_instance_id', return_value=['site_url'])
    @patch.object(CourseIndexView, 'is_current_user_member_of_course_staff', return_value=False)
    @patch("canvas_course_wizard.views.super", create=True)
    def test_get_context_data_course_creation_as_non_staff_with_course_sites(self, mock_super, mock_staffer, mock_course_urls):
        mock_super.return_value.get_context_data.return_value = {}
        context = self.view.get_context_data()
        self.assertEquals(context['user_can_create_course'], False,
                          'User should not be able to create course if they are not a staff member')

    @patch.object(CourseIndexView, 'get_urls_from_course_instance_id', return_value=['site_url'])
    @patch.object(CourseIndexView, 'is_current_user_member_of_course_staff', return_value=True)
    @patch("canvas_course_wizard.views.super", create=True)
    def test_get_context_data_course_creation_as_staff_with_course_sites(self, mock_super, mock_staffer, mock_course_urls):
        mock_super.return_value.get_context_data.return_value = {}
        context = self.view.get_context_data()
        self.assertEquals(context['user_can_create_course'], False,
                          'User should not be able to create course if there are offical course sites')

    @patch.object(CourseIndexView, 'get_urls_from_course_instance_id', return_value=None)
    @patch.object(CourseIndexView, 'is_current_user_member_of_course_staff', return_value=True)
    @patch("canvas_course_wizard.views.super", create=True)
    def test_get_context_data_course_creation_as_staff_with_no_course_sites(self, mock_super, mock_staffer, mock_course_urls):
        mock_super.return_value.get_context_data.return_value = {}
        context = self.view.get_context_data()
        self.assertEquals(context['user_can_create_course'], True,
                          'User should be able to create course if they are staff and no course sites already exist')
