import unittest
#import mock
from .views import CourseWizardIndexView
from django.core.urlresolvers import reverse, resolve
#from django.test import RequestFactory
# Create your tests here.


class CourseWizardIndexViewTest(unittest.TestCase):

    def test_route_by_name(self):
        url = reverse('crs-wiz:wizard-index')
        self.assertEqual(url, '/ext_tools/course_wizard/')

    def test_route_to_view(self):
        match = resolve('/ext_tools/course_wizard/')
        self.assertEquals('CourseWizardIndexView', match.func.__name__)
        self.assertTrue(len(match.args) == 0, 'Should be no args for course wizard index view')
        self.assertTrue(len(match.kwargs) == 0, 'Should be no kwargs for course wizard index view')

    def test_template_setup(self):
        view = CourseWizardIndexView()
        self.assertTrue(view.template_name)
        self.assertEquals(view.template_name, 'canvas_course_wizard/index.html')

# Create your tests here.
