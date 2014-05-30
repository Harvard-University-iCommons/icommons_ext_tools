import unittest
from django.core.urlresolvers import resolve
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin
from django.test import RequestFactory
from django.shortcuts import render
from .views import CourseWizardIndexView


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
