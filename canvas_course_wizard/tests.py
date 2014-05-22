import unittest
import mock
from .views import CourseWizardIndexView, CourseIndexView
from .mixins import Custom404Mixin
from django.core.urlresolvers import resolve
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from braces.views import LoginRequiredMixin
from django.test import RequestFactory
from icommons_common.models import CourseInstance
from django.shortcuts import render
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404


class Custom404MixinTest(unittest.TestCase):
    longMessage = True

    def setUp(self):
        self.mixin = Custom404Mixin()

    def test_instance_setup(self):
        self.assertEqual(self.mixin.template_name_404, None,
                         "Custom404Mixin should have default template name attribute set to None")

    def test_get_404_template_names_none_template_raises_improperly_configured(self):
        with self.assertRaises(ImproperlyConfigured):
            self.mixin.get_404_template_names()

    def test_get_404_template_names_result_matches_template_attribute(self):
        template_name_404 = 'canvas_course_wizard/my_custom_404_page.html'
        self.mixin.template_name_404 = template_name_404
        self.assertEqual(self.mixin.get_404_template_names(), [template_name_404],
                         "Template result should be a list containing defined class attribute")

    @mock.patch('canvas_course_wizard.mixins.super', create=True)
    @mock.patch('canvas_course_wizard.mixins.TemplateResponse')
    def test_dispatch_response_when_404_raised(self, template_response_mock, super_mock):
        request = RequestFactory().get('/fake-path')
        get_404_template_names_mock = mock.Mock()
        # Ensure call to super.dispatch raises a 404
        super_mock.return_value.dispatch.side_effect = Http404
        self.mixin.get_404_template_names = get_404_template_names_mock
        response = self.mixin.dispatch(request)
        self.assertEqual(response, template_response_mock,
                         "Return value of dispatch when 404 is raised should be a TemplateResponse object")
        get_404_template_names_mock.assert_called_once_with()
        template_response_mock.assert_called_with(status=404, request=request, template=mock.ANY)

    @mock.patch('canvas_course_wizard.mixins.super', create=True)
    def test_dispatch_response_when_404_not_raised(self, super_mock):
        request = RequestFactory().get('/fake-path')
        response = self.mixin.dispatch(request)
        # Little trick here to ensure that a call to the dispatch method normally
        # returns the result of super.dispatch
        self.assertEqual(response, super_mock.return_value.dispatch.return_value,
                         "Call to dispatch that doesn't raise an exception should return result super().dispatch()")


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
        self.assertIsInstance(view, TemplateView,
                              'Wizard index view should be a subclass of TemplateView')
        self.assertIsInstance(view, LoginRequiredMixin,
                              'Wizard index view should implement the LoginRequiredMixin')
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
        self.assertEqual(match.kwargs['pk'], '123',
                         'Keyword argument \'pk\' should match end of url')

    def test_view_instance_setup(self):
        view = CourseIndexView()
        self.assertIsInstance(view, DetailView,
                              'Wizard index view expected to be a subclass of DetailView')
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
            # Set up the patch mocks
            mock_super.return_value.get_context_data.return_value = {}
            # Make the call
            context = view.get_context_data()

        mock_is_staffer.assert_called_once_with(mock_ci.course_instance_id)
        self.assertTrue(context['show_create'],
                        'A teaching staffer for a non-canvas course should be able to create')

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
