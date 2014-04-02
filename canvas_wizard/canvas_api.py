
import pprint
import requests
import logging
import httplib
import json
from secure import SECURE_SETTINGS
#httplib.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig() 
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


pp = pprint.PrettyPrinter(indent=4)

AUTH_TOKEN = 'Bearer %s' % SECURE_SETTINGS.get('TOKEN')
HEADERS = {'Authorization ': AUTH_TOKEN}
CANVAS_SERVER_BASE_URL = SECURE_SETTINGS.get('CANVAS_SERVER_BASE_URL')


class Canvasapi(object):
    """
    Class
    """

    def __init__(self):
        self.data = []

    @classmethod
    def add_content_to_page(cls, course_id, page, body):
        """
        Add Content to page
        """
        payload = {'wiki_page[body]': body}
        page_url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/pages/'+page
        req = requests.put(page_url, data=payload, headers=HEADERS)
        pp.pprint(req.text)

    @classmethod
    def get_account_courses(cls, account_id):
        """
        Add Content to page
        """
        payload = {
            #'wiki_page[body]': body
        }
        page_url = CANVAS_SERVER_BASE_URL+'/api/v1/accounts/'+account_id+'/courses'
        req = requests.get(page_url, data=payload, headers=HEADERS)
        courses = json.loads(req.text)
        print '{0:2} {1:15} {2}'.format('id', 'course code', 'course name')
        print '----------------------------------------------------'
        for course in courses:
            print '{0:2} {1:15} {2}'.format(course.get('id'), course.get('course_code'), course.get('name'))
        #pp.pprint(req.text)

    @classmethod
    def hide_page_from_students(cls, course_id, page):
        """
        Add Content to page
        """
        payload = {
            'wiki_page[hide_from_students]': 'true'
        }
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/pages/'+page
        req = requests.put(url, data=payload, headers=HEADERS)
        pp.pprint(req.text)

    @classmethod
    def set_tab_hidden(cls, course_id, tab, hidden):
        """
        disable tab
        """
        payload = {'hidden' : hidden}
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/tabs/'+tab
        req = requests.put(url, data=payload, headers=HEADERS)
        pp.pprint(req.text)

    @classmethod
    def set_tab_visibility(cls, course_id, tab, visibility):
        """
        disable tab
        """
        payload = {'visibility' : visibility}
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/tabs/'+tab
        req = requests.put(url, data=payload, headers=HEADERS)
        pp.pprint(req.text)

    @classmethod
    def show_tabs(cls, course_id):
        """
        disable tab
        """
        payload = {
            #'hidden' : visibility
            }
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/tabs?include=external'
        req = requests.get(url, data=payload, headers=HEADERS)
        tabs = json.loads(req.text)
        print '{0:25} {1:20} {2:6} {3:10} {4:10} {5}'.format('id', 'label', 'hidden', 'visibility', 'type', 'position')
        print '----------------------------------------------------'
        if len(tabs) > 0:
            for tab in tabs:
                hidden = str(tab.get('hidden', 'False'))
                print '{0:25} {1:20} {2:6} {3:10} {4:10} {5}'.format(tab.get('id'), tab.get('label'), hidden, tab.get('visibility'), tab.get('type'), tab.get('position'))

    @classmethod
    def update_course_syllabus_body(cls, course_id, body):
        """
        update course
        """
        payload = {'course[syllabus_body]': body}
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id
        req = requests.put(url, data=payload, headers=HEADERS)
        pp.pprint(req.text)

    @classmethod
    def create_course_content_migration(cls, source_course_id, course_id):
        """
        copy course content
        """
        payload = {
            'migration_type' : 'course_copy_importer',
            'settings[question_bank_name]' : 'importquestions',
            'settings[source_course_id]' : source_course_id,
            #'pre_attachment[name]' : 'mycourse.imscc',
        }
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/content_migrations'
        req = requests.post(url, data=payload, headers=HEADERS)
        pp.pprint(req.text)

    @classmethod
    def list_content_migrations(cls, course_id):
        """
        list all course migrations
        """
        payload = { 
            'migration_type' : 'common_cartridge_importer',
            'pre_attachment[name]' : 'mycourse.imscc',
        }
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/content_migrations'
        req = requests.post(url, data=payload, headers=HEADERS)
        pp.pprint(req.text)

    @classmethod
    def get_content_migration(cls, course_id, migration_id):
        """
        get course migration info
        """
        payload = { 
            #'migration_type' : 'common_cartridge_importer',
            #'pre_attachment[name]' : 'mycourse.imscc',
        }
        url = CANVAS_SERVER_BASE_URL+'/api/v1/courses/'+course_id+'/content_migrations/'+migration_id
        req = requests.get(url, data=payload, headers=HEADERS)
        pp.pprint(req.text)






