import unittest
import mock
from .views import CourseWizardIndexView
# Create your tests here.


class CustomViewTest(unittest.TestCase):
    def test_template_call(self):
        view = CourseWizardIndexView.as_view()
        request = mock.MagicMock(name='request')
        request.method.lower.return_value = 'get'
        # mock_view.request.user.is_authenticated = lambda: True
        # mock_view.request.method.lower = lambda: u'get'
        #view.response_class = mock.Mock(name='response_class')
        print request.method.lower()
        response = view(request, None, None)
        response.render()
        print request.mock_calls
        #print view.response_class.mock_calls[0]

# Create your tests here.
