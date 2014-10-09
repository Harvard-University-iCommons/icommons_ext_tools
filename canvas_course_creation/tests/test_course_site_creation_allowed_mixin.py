import unittest
import mock
from django.test import RequestFactory
from .mixins import CourseSiteCreationAllowedMixin
from django.http import Http404


class CourseSiteCreationAllowedMixinTest(unittest.TestCase):
    longMessage = True

    def setUp(self):
        self.mixin = CourseSiteCreationAllowedMixin()

    # TODO: Add in unit tests for mixin
    def test_true(self):
        self.assertEqual(1, 1)
