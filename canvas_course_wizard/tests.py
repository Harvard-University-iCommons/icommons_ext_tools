import unittest
import mock
from .views import CourseWizardIndexView, CourseIndexView
from django.core.urlresolvers import reverse, resolve
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin
from django.test import RequestFactory
from django.core.urlresolvers import NoReverseMatch
from icommons_common.models import CourseInstance, SiteMap, CourseSite
from django.shortcuts import render
from django.conf import settings


class CourseWizardIndexViewTest(unittest.TestCase):
    longMessage = True

    def test_resolve_route_to_view(self):
        match = resolve('/', 'canvas_course_wizard.urls')
        self.assertEqual(match.view_name, 'wizard-index',
                         "named-url for wizard index didn't match expected result")
        self.assertEqual('CourseWizardIndexView', match.func.__name__)
        self.assertEqual(len(match.args), 0, 'Should be no args for course wizard index view')
        self.assertEqual(len(match.kwargs), 0, 'Should be no kwargs for course wizard index view')

    def test_view_instance_setup(self):
        view = CourseWizardIndexView()
        self.assertIsInstance(
            view, TemplateView, 'Wizard index view should be a subclass of TemplateView')
        self.assertIsInstance(
            view, LoginRequiredMixin, 'Wizard index view should implement the LoginRequiredMixin')
        self.assertEquals(view.template_name, 'canvas_course_wizard/index.html')

    def test_template_render(self):
        request = RequestFactory().get('/fake-path')
        template_name = 'canvas_course_wizard/index.html'
        result = render(request, template_name)
        self.assertEquals(result.status_code, 200, 'Wizard index view should render successfully')


class CourseIndexViewTest(unittest.TestCase):
    longMessage = True

    def setUp(self):
        self.request = RequestFactory().get('/fake-path')

    def test_resolve_route_to_view(self):
        match = resolve('/courses/123/', 'canvas_course_wizard.urls')
        self.assertEqual(match.view_name, 'course-index',
                         "named-url for course index didn't match expected result")
        self.assertEqual('CourseIndexView', match.func.__name__)
        self.assertEqual(len(match.args), 0, 'Should be no args for course wizard index view')
        self.assertEqual(len(match.kwargs), 1, 'Should be one keyword argument for course index')
        self.assertEqual(
            match.kwargs['pk'], '123', 'Keyword argument \'pk\' should match end of url')

    def test_view_instance_setup(self):
        view = CourseIndexView()
        self.assertIsInstance(
            view, DetailView, 'Wizard index view expected to be a subclass of DetailView')
        self.assertEquals(view.template_name, 'canvas_course_wizard/course.html')
        self.assertIs(view.model, CourseInstance, 'Model lookup type should be CourseInstance')
        self.assertEqual(view.context_object_name, 'course',
                         "context should reference the course instance as 'course'")

    '''
    Expectation entering the get_context_data is that the object has been found... a 404 error would have been
    raised before getting to this method, so we'll do the minimal setup required
    '''

    def test_get_context_data_for_non_canvas_course_as_teaching_staff(self):

        # Make sure user is considered a staff member
        mock_is_staffer = mock.Mock(name='is_staffer', return_value=True)
        # Course instance to use for test
        mock_ci = CourseInstance(course_instance_id=9999)

        view = CourseIndexView()
        view.request = self.request
        view.object = mock_ci
        view.is_current_user_member_of_course_staff = mock_is_staffer

        with mock.patch('canvas_course_wizard.views.super', create=True) as mock_super:
            with mock.patch('canvas_course_wizard.views.SiteMap.objects.get') as mock_sitemap:
                # Set up the patch mocks
                mock_super.return_value.get_context_data.return_value = {}
                # Make the call
                context = view.get_context_data()

        mock_is_staffer.assert_called_once_with(mock_ci.course_instance_id)
        self.assertTrue(
            context['show_create'], 'A teaching staffer for a non-canvas course should be able to create')

    def test_find_isite_from_course_instance_id(self):

        error_message = 'Given a course instance_id that has an isite setup, the url to the isite should be constructed and returned in the context'
        # Make sure user is considered a staff member
        mock_is_staffer = mock.Mock(name='is_staffer', return_value=True)
        # Course instance to use for test
        mock_ci = CourseInstance(course_instance_id=9999)

        view = CourseIndexView()
        view.request = self.request
        view.object = mock_ci
        view.is_current_user_member_of_course_staff = mock_is_staffer
        with mock.patch('canvas_course_wizard.views.super', create=True) as mock_super:
            with mock.patch('canvas_course_wizard.views.SiteMap.objects.get') as mock_sitemap:
                # mock_sitemap.return_value

                # set the return value for the mocked database call
                mock_sitemap().course_site.external_id = 'k12345'

                mock_super.return_value.get_context_data.return_value = {}

                # Make the call
                context = view.get_context_data()

        self.assertEquals(
            context['isite_course_url'], 'http://isites.harvard.edu/k12345', error_message)

    # def test_isite_url_or_false(self):
    #     with mock.patch('canvas_course_wizard.views.SiteMap') as my_model_mock:

    #         mock_ci = CourseInstance(course_instance_id=211144)

    #         view = CourseIndexView()
    #         view.request = self.request
    #         view.object = mock_ci

    #         my_model_mock.objects = mock.Mock()

    #         conf = {'get.side_effect': SiteMap.DoesNotExist}
    #         my_model_mock.objects.configure_mock(**conf)
    #         self.assertFalse(view.get_isite_url_or_false(211144))

    #         conf = {'get.return_value': mock.Mock()}
    #         my_model_mock.objects.configure_mock(**conf)
    #         self.assertTrue(view.get_isite_url_or_false(211144))

    # def test_get_canvas_url_or_false(self):
    #    pass


    # def test_get_context_data_for_non_existing_course(self):
    # For this method, self.object is expected to be an attribute so it's being defaulted to None here.  In
    # Django 1.7 branch the assumption is now conditionalized.
    #     view = CourseCatalogIndexView()
    #     view.request = self.request
    #     view.kwargs = {'school': 'ext', 'registrar_code': '21197', 'year': 2014, 'term': 'Fall'}

    #     with mock.patch('canvas_course_wizard.views.CourseInstance.objects.get') as mock_db_course_get:
    #         with mock.patch('canvas_course_wizard.views.super', create=True) as mock_super:

    #             mock_db_course_get.side_effect = CourseInstance.DoesNotExist
    #             mock_super.return_value.get_context_data.return_value = {}
    #             context = view.get_context_data()

    #     self.assertEquals(len(context), 0)
    #     mock_db_course_get.assert_called_once_with(
    #         course__registrar_code='21197',
    #         term__school_id='ext',
    #         term__academic_year=2014,
    #         term__term_code__term_name__startswith='Fall'
    #     )
    #     self.assertEquals(view.template_name, 'canvas_course_wizard/course_not_found.html')

    # def test_render_catalog_template(self):
    #     template_name = 'canvas_course_wizard/course_catalog.html'
    #     result = render(self.request, template_name)
    #     self.assertEquals(result.status_code, 200)

    # def test_render_course_not_found_template(self):
    #     template_name = 'canvas_course_wizard/course_not_found.html'
    #     result = render(self.request, template_name)
    #     self.assertEquals(result.status_code, 200)
