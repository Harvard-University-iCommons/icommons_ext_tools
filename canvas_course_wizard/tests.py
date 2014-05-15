import unittest
import mock
from .views import CourseWizardIndexView, CourseCatalogIndexView
from django.core.urlresolvers import reverse, resolve
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin
from django.test import RequestFactory
from django.core.urlresolvers import NoReverseMatch
from icommons_common.models import CourseInstance
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist


class CourseWizardIndexViewTest(unittest.TestCase):
    longMessage = True

    def test_route_to_view(self):
        match = resolve('/', 'canvas_course_wizard.urls')
        self.assertEqual(match.view_name, 'wizard-index', "named-url for wizard index didn't match expected result")
        self.assertEqual('CourseWizardIndexView', match.func.__name__)
        self.assertEqual(len(match.args), 0, 'Should be no args for course wizard index view')
        self.assertEqual(len(match.kwargs), 0, 'Should be no kwargs for course wizard index view')

    def test_view_instance(self):
        view = CourseWizardIndexView()
        self.assertIsInstance(view, TemplateView, 'Wizard index view should be a subclass of TemplateView')
        self.assertIsInstance(view, LoginRequiredMixin, 'Wizard index view should implement the LoginRequiredMixin')
        self.assertEquals(view.template_name, 'canvas_course_wizard/index.html')

    def test_template_render(self):
        request = RequestFactory().get('/fake-path')
        template_name = 'canvas_course_wizard/index.html'
        result = render(request, template_name)
        self.assertEquals(result.status_code, 200, 'Wizard index view should render successfully')
            

class CourseCatalogIndexViewTest(unittest.TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_route_by_name(self):
        url = reverse(
            'crs-wiz:course-catalog',
            kwargs={'school': 'ext', 'registrar_code': 21197, 'year': 2014, 'term': 'Fall'}
        )
        self.assertEqual(url, '/ext_tools/course_wizard/catalog/ext/21197/2014/Fall')

    def test_route_not_enough_args(self):
        self.assertRaises(
            NoReverseMatch,
            reverse,
            'crs-wiz:course-catalog',
            kwargs={'school': 'ext', 'registrar_code': 21197}
        )

    def test_route_invalid_year_kwarg(self):
        self.assertRaises(
            NoReverseMatch,
            reverse,
            'crs-wiz:course-catalog',
            kwargs={'school': 'ext', 'registrar_code': '21197', 'year': 14, 'term': 'Fall'}
        )

    def test_route_to_view(self):
        match = resolve('/ext_tools/course_wizard/catalog/ext/21197/2014/Fall')
        self.assertEquals(match.view_name, 'crs-wiz:course-catalog')
        self.assertEquals(CourseCatalogIndexView.__name__, match.func.__name__)
        self.assertTrue(len(match.args) == 0, 'Should be no args for course wizard index view')
        self.assertEquals(len(match.kwargs), 4)
        self.assertEquals(match.kwargs['school'], 'ext')
        self.assertEquals(match.kwargs['registrar_code'], '21197')
        self.assertEquals(match.kwargs['year'], '2014')
        self.assertEquals(match.kwargs['term'], 'Fall')

    def test_get_context_data_for_existing_course(self):
        selected_course = CourseInstance()
        mock_course_instance = mock.Mock(name='course-instance')
        mock_course_instance.objects.get.return_value = selected_course

        request = self.factory.get('/fake-path')
        # For this method, self.object is expected to be an attribute so it's being defaulted to None here.  In
        # Django 1.7 branch the assumption is now conditionalized.
        view = CourseCatalogIndexView()
        view.request = request
        view.kwargs = {'school': 'ext', 'registrar_code': '21197', 'year': 2014, 'term': 'Fall'}

        with mock.patch('canvas_course_wizard.views.CourseInstance', mock_course_instance):
            context = view.get_context_data()

        self.assertEquals(context['course'], selected_course)
        mock_course_instance.objects.get.assert_called_once_with(
            course__registrar_code='21197',
            term__school_id='ext',
            term__academic_year=2014,
            term__term_code__term_name__startswith='Fall'
        )
        self.assertEquals(view.template_name, 'canvas_course_wizard/course_catalog.html')

    def test_get_context_data_for_non_existing_course(self):
        mock_course_instance = mock.Mock(name='course-instance')
        mock_course_instance.objects.get.side_effect = ObjectDoesNotExist('blah')

        request = self.factory.get('/fake-path')
        # For this method, self.object is expected to be an attribute so it's being defaulted to None here.  In
        # Django 1.7 branch the assumption is now conditionalized.
        view = CourseCatalogIndexView()
        view.request = request
        view.kwargs = {'school': 'ext', 'registrar_code': 'bogus', 'year': 1999, 'term': 'Fall'}

        with mock.patch('canvas_course_wizard.views.CourseInstance', mock_course_instance):
            context = view.get_context_data()
            # mock_course_instance.objects.get.assert_called_once_with(
            #     course__registrar_code='bogus',
            #     term__school_id='ext',
            #     term__academic_year=1999,
            #     term__term_code__term_name__startswith='Fall'
            # )
        #print context
        #self.assertEquals(len(context), 0)
        self.assertEquals(view.template_name, 'canvas_course_wizard/course_not_found.html')


# Create your tests here.
