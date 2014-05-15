import unittest
import mock
from .views import CourseWizardIndexView#, CourseIndexView
from django.core.urlresolvers import reverse, resolve
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin
from django.test import RequestFactory
from django.core.urlresolvers import NoReverseMatch
from icommons_common.models import CourseInstance
from django.shortcuts import render


class CourseWizardIndexViewTest(unittest.TestCase):
    longMessage = True

    def test_route_to_view(self):
        match = resolve('/', 'canvas_course_wizard.urls')
        self.assertEqual(match.view_name, 'wizard-indx', "named-url for wizard index didn't match expected result")
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
            

# class CourseCatalogIndexViewTest(unittest.TestCase):

#     def setUp(self):
#         self.request = RequestFactory().get('/fake-path')

#     def test_route_by_name(self):
#         url = reverse(
#             'crs-wiz:course-catalog',
#             kwargs={'school': 'ext', 'registrar_code': 21197, 'year': 2014, 'term': 'Fall'}
#         )
#         self.assertEqual(url, '/ext_tools/course_wizard/catalog/ext/21197/2014/Fall')

#     def test_route_not_enough_args(self):
#         self.assertRaises(
#             NoReverseMatch,
#             reverse,
#             'crs-wiz:course-catalog',
#             kwargs={'school': 'ext', 'registrar_code': 21197}
#         )

#     def test_route_invalid_year_kwarg(self):
#         self.assertRaises(
#             NoReverseMatch,
#             reverse,
#             'crs-wiz:course-catalog',
#             kwargs={'school': 'ext', 'registrar_code': '21197', 'year': 14, 'term': 'Fall'}
#         )

#     def test_route_to_view(self):
#         match = resolve('/ext_tools/course_wizard/catalog/ext/21197/2014/Fall')
#         self.assertEquals(match.view_name, 'crs-wiz:course-catalog')
#         self.assertEquals(CourseCatalogIndexView.__name__, match.func.__name__)
#         self.assertTrue(len(match.args) == 0, 'Should be no args for course wizard index view')
#         self.assertEquals(len(match.kwargs), 4)
#         self.assertEquals(match.kwargs['school'], 'ext')
#         self.assertEquals(match.kwargs['registrar_code'], '21197')
#         self.assertEquals(match.kwargs['year'], '2014')
#         self.assertEquals(match.kwargs['term'], 'Fall')

#     def test_get_context_data_for_existing_course(self):
#         selected_course = CourseInstance()
#         # For this method, self.object is expected to be an attribute so it's being defaulted to None here.  In
#         # Django 1.7 branch the assumption is now conditionalized.
#         view = CourseCatalogIndexView()
#         view.request = self.request
#         view.kwargs = {'school': 'ext', 'registrar_code': '21197', 'year': 2014, 'term': 'Fall'}

#         with mock.patch('canvas_course_wizard.views.CourseInstance.objects.get') as mock_db_course_get:
#             with mock.patch('canvas_course_wizard.views.super', create=True) as mock_super:
#                 # Set up the mocks
#                 mock_db_course_get.return_value = selected_course
#                 mock_super.return_value.get_context_data.return_value = {}
#                 # Make the call
#                 context = view.get_context_data()

#         self.assertEquals(context['course'], selected_course)
#         mock_db_course_get.assert_called_once_with(
#             course__registrar_code='21197',
#             term__school_id='ext',
#             term__academic_year=2014,
#             term__term_code__term_name__startswith='Fall'
#         )
#         self.assertEquals(view.template_name, 'canvas_course_wizard/course_catalog.html')

#     def test_get_context_data_for_non_existing_course(self):
#         # For this method, self.object is expected to be an attribute so it's being defaulted to None here.  In
#         # Django 1.7 branch the assumption is now conditionalized.
#         view = CourseCatalogIndexView()
#         view.request = self.request
#         view.kwargs = {'school': 'ext', 'registrar_code': '21197', 'year': 2014, 'term': 'Fall'}

#         with mock.patch('canvas_course_wizard.views.CourseInstance.objects.get') as mock_db_course_get:
#             with mock.patch('canvas_course_wizard.views.super', create=True) as mock_super:

#                 mock_db_course_get.side_effect = CourseInstance.DoesNotExist
#                 mock_super.return_value.get_context_data.return_value = {}
#                 context = view.get_context_data()

#         self.assertEquals(len(context), 0)
#         mock_db_course_get.assert_called_once_with(
#             course__registrar_code='21197',
#             term__school_id='ext',
#             term__academic_year=2014,
#             term__term_code__term_name__startswith='Fall'
#         )
#         self.assertEquals(view.template_name, 'canvas_course_wizard/course_not_found.html')

#     def test_render_catalog_template(self):
#         template_name = 'canvas_course_wizard/course_catalog.html'
#         result = render(self.request, template_name)
#         self.assertEquals(result.status_code, 200)

#     def test_render_course_not_found_template(self):
#         template_name = 'canvas_course_wizard/course_not_found.html'
#         result = render(self.request, template_name)
#         self.assertEquals(result.status_code, 200)
