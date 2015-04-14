"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from unittest import skip
from django.contrib.auth.models import User
#from icommons_common.models import School, CourseInstance, Template, TemplateAccessList, TemplateUsers, TemplateAccount, TemplateCourseDelegates
from django.test import TestCase, RequestFactory
from .models import Template, TemplateAccessList, TemplateUsers, TemplateAccount, TemplateCourseDelegates
from .views import launch

#import unittest
#import mock
# Create your tests here.

@skip("Can't test since unmanaged models cannot be instantiated")
class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.user = User(username='20533064', email='eric_parker@harvard.edu', password='top_secret')
        TemplateUsers.objects.create()

    def test_details(self):
        # Create an instance of a GET request.
        # /course_setup/ext/21144/2012/Spring
        #request = self.factory.get('/course_setup/ext/21144/2012/Spring')
        request = self.factory.get('/launch')
        request.session = {}
        request.session['huid'] = '20533064'
        request.user = self.user
        school = 'ext'
        registrar_code = '21144'
        year = '2012'
        term = 'Spring'

        # Test my_view() as if it were deployed at /customer/details
        #response = course_setup(request, school, registrar_code, year, term)
        response = launch(request)
        self.assertEqual(response.status_code, 200)


