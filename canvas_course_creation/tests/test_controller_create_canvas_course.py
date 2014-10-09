from unittest import TestCase
from mock import patch, ANY, DEFAULT, Mock, MagicMock
from canvas_course_creation.controller import get_course_data,create_canvas_course,create_new_course
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.test import TestCase

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

 
@patch.multiple('canvas_course_creation.controller', 
    get_course_data = DEFAULT, create_course_section = DEFAULT, create_new_course = DEFAULT)


class CreateCanvasCourseTest(TestCase):
    longMessage = True

    def setUp(self):
        self.sis_course_id = "305841"

    def  get_mock_of_get_course_data(self):
        course_model_mock = MagicMock( sis_account_id="school:gse",
            course_code = "GSE ",
            course_name = "GSE test course",
            sis_term_id = "gse term",
            primary_section_name = "Primary section")
        return course_model_mock
    
    @patch('canvas_course_creation.controller.create_canvas_course')
    def test_create_canvas_course_method_called_with_rigth_params(self, 
        create_canvas_course, get_course_data, create_course_section, create_new_course ):
        '''
        Test that controller makes create_canvas_course call with expected args
        '''  
        result = create_canvas_course(self.sis_course_id)    
        create_canvas_course.assert_called_with(self.sis_course_id)
        
        
    def test_get_course_data_method_called_with_rigth_params(self, get_course_data, 
        create_course_section, create_new_course ):
        '''
        Test that controller method makes a call to get_course_data api with expected args
        '''        
        create_canvas_course(self.sis_course_id)
        get_course_data.assert_called_with(self.sis_course_id)

    def test_exception_in_get_course_data(self, get_course_data, create_course_section, 
        create_new_course):
        '''
        Test that an exception is raised when get_course_data throws an exception
        '''
        create_canvas_course(self.sis_course_id)
        get_course_data.side_effect = Exception
        self.assertRaises(Exception, get_course_data,self.sis_course_id)

    def test_object_not_found_exception_in_get_course_data(self, get_course_data,
         create_course_section, create_new_course):
        '''
        Test  when get_course_data throws an ObjectDoesNotExist
        Note: Http404 exception is one of the exceptions not visible to the test client. 
        So just checking for ObjectDoesNotExist
        '''
        create_canvas_course(self.sis_course_id)
        get_course_data.side_effect = ObjectDoesNotExist
        self.assertRaises(ObjectDoesNotExist, get_course_data,self.sis_course_id)

    @patch('canvas_course_creation.controller.logger.error')
    def test_object_not_found_exception_in_get_course_data_logs_error(self, log_replacement,
            get_course_data, create_course_section, create_new_course):
        '''
        Test that the logger.error logs error when when get_course_data throws an ObjectDoesNotExist
        '''
        create_canvas_course(self.sis_course_id)
        get_course_data.side_effect = ObjectDoesNotExist
        log_replacement.assert_called()

    @patch('canvas_course_creation.controller.SDK_CONTEXT')
    def test_create_new_course_method_is_called(self, SDK_CONTEXT, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_new_course method is called by create_canvas_course 
        controller method
        '''
        create_new_course.return_value = DEFAULT
        create_canvas_course(self.sis_course_id)
        create_new_course.assert_called(ANY,ANY, ANY, ANY, ANY, ANY)


    def test_when_create_new_course_method_raises_exception(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that an exception is raised when the create_new_course method 
        throws an exception
        '''
        create_new_course.side_effect = Exception
        self.assertRaises( Exception, create_canvas_course, self.sis_course_id)


    def test_create_new_course_method_is_called_with_account_id(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_new_course method is called with account_id kwarg
        '''
        account_id = 'school:gse'
        course_model_mock = self.get_mock_of_get_course_data()
        get_course_data.return_value = course_model_mock
        result = create_canvas_course(self.sis_course_id)
        args, kwargs = create_new_course.call_args
        self.assertEqual(kwargs.get('account_id'), 'sis_account_id:'+account_id)

    def test_create_new_course_method_is_called_with_course_code(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_new_course method is called is called with course_code kwarg
        '''
        course_code = "GSE "
        course_model_mock = self.get_mock_of_get_course_data()
        get_course_data.return_value = course_model_mock
        result = create_canvas_course(self.sis_course_id)
        args, kwargs = create_new_course.call_args
        self.assertEqual(kwargs.get('course_course_code'), course_code)

    def test_create_new_course_method_is_called_with_course_name(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_new_course method is called with course name kwarg
        '''
        course_name = 'GSE test course'
        course_model_mock = self.get_mock_of_get_course_data()
        get_course_data.return_value = course_model_mock
        result = create_canvas_course(self.sis_course_id)
        args, kwargs = create_new_course.call_args
        self.assertEqual(kwargs.get('course_name'), course_name)

    def test_create_new_course_method_is_called_with_course_term_id(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_new_course method is called with course_term_id kwarg
        '''
        course_term_id = 'gse term'
        course_model_mock = self.get_mock_of_get_course_data()
        get_course_data.return_value = course_model_mock
        result = create_canvas_course(self.sis_course_id)
        args, kwargs = create_new_course.call_args
        self.assertEqual(kwargs.get('course_term_id'), course_term_id)

    def test_create_new_course_method_is_called_with_sis_course_id(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_new_course method is called with course_sis_course_id  kwarg
        '''
        result = create_canvas_course(self.sis_course_id)
        args, kwargs = create_new_course.call_args
        self.assertEqual(kwargs.get('course_sis_course_id'), self.sis_course_id)
   
    @patch('canvas_course_creation.controller.SDK_CONTEXT')
    def test_create_course_section_method_is_called(self, SDK_CONTEXT, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_new_course method is called by create_canvas_course controller method
        '''
        create_course_section.return_value = DEFAULT
        create_canvas_course(self.sis_course_id)
        create_course_section.assert_called(ANY, ANY, ANY, ANY)

    def test_create_course_section_method_is_called_with_section_name(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_course_section SDK method is called with course_section_name kwarg
        '''
        primary_section_name = 'Primary section'

        course_model_mock = self.get_mock_of_get_course_data()
        get_course_data.return_value = course_model_mock
        result = create_canvas_course(self.sis_course_id)
        args, kwargs = create_course_section.call_args
        self.assertEqual(kwargs.get('course_section_name'), primary_section_name)

    def test_create_course_section_method_is_called_with_sis_section_id(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that create_course_section SDK method is called with sis_section_id kwarg
        '''
        result = create_canvas_course(self.sis_course_id)
        args, kwargs = create_course_section.call_args
        self.assertEqual(kwargs.get('course_section_sis_section_id'), self.sis_course_id)

    def test_when_create_course_section_method_raises_exception(self, get_course_data,
     create_course_section, create_new_course):
        '''
        Test to assert that an exception is raised when the ccreate_course_section method 
        throws an exception
        '''
        create_course_section.side_effect = Exception
        self.assertRaises( Exception, create_canvas_course, self.sis_course_id)
