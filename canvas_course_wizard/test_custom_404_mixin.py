import unittest
import mock
from django.test import RequestFactory
from .mixins import Custom404Mixin
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.template.response import TemplateResponse


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
    @mock.patch('canvas_course_wizard.mixins.TemplateResponse', spec=TemplateResponse)
    def test_dispatch_response_when_404_raised(self, template_response_mock, super_mock):
        request = RequestFactory().get('/fake-path')
        get_404_template_names_mock = mock.Mock()
        # Ensure call to super.dispatch raises a 404
        super_mock.return_value.dispatch.side_effect = Http404
        self.mixin.get_404_template_names = get_404_template_names_mock
        response = self.mixin.dispatch(request)
        self.assertEqual(response, template_response_mock.return_value,
                         "Return value of dispatch when 404 is raised should be a TemplateResponse()")
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
