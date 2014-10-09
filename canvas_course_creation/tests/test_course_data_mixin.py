import unittest
import mock
from django.test import RequestFactory
from .mixins import CourseDataMixin
from django.http import Http404


class CourseDataMixinTest(unittest.TestCase):
    longMessage = True

    def setUp(self):
        self.mixin = CourseDataMixin()

    # TODO: Add in unit tests for mixin
    def test_true(self):
        self.assertEqual(1, 1)
