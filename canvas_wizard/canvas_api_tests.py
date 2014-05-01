from  canvas_api import Canvasapi
import sys

def main():
    """
    main
    """
    testnum = 100
    instance = Canvasapi()

    print "*********************************************"
    print " 1 - set navigation tab hidden"
    print " 2 - update course syllabus body"
    print " 3 - hide page from students"
    print " 4 - add content to page"
    print " 5 - create course content migration (copy course)"
    print " 6 - list content migrations"
    print " 7 - get content migration"
    print " 8 - show tabs"
    print " 9 - set navigation tab visibility"
    print " 10 - get account courses"
    print " 11 - upload file"
    print " 0 - exit "
    print "*********************************************"

    
    #print "course id set to "+course_id

    while testnum != 0:
        testnum = raw_input('Enter test number: ')
        if testnum == str(1):
            course_id = raw_input('Enter a course_id: ')
            tab_id = raw_input('Enter tab id: ')
            visible = raw_input('Enter value for hidden (true or false): ')
            instance.set_tab_hidden(course_id, tab_id, visible)
        elif testnum == str(2):
            course_id = raw_input('Enter a course_id: ')
            content = raw_input('Enter some text: ')
            instance.update_course_syllabus_body(course_id, content)
        elif testnum == str(3):
            course_id = raw_input('Enter a course_id: ')
            page_id = raw_input('Enter page id: ')
            instance.hide_page_from_students(course_id, page_id)
        elif testnum == str(4):
            course_id = raw_input('Enter a course_id: ')
            page_id = raw_input('Enter page id: ')
            content = raw_input('Enter some text: ')
            instance.add_content_to_page(course_id, page_id, content)
        elif testnum == str(5):
            source_course_id = raw_input('Enter a source course_id: ')
            course_id = raw_input('Enter the new course_id: ')
            instance.create_course_content_migration(source_course_id, course_id)
        elif testnum == str(6):
            course_id = raw_input('Enter a course_id: ')
            instance.list_content_migrations(course_id)
        elif testnum == str(7):
            course_id = raw_input('Enter a course_id: ')
            migration_id = raw_input('Enter migration id: ')
            instance.get_content_migration(course_id, migration_id)
        elif testnum == str(8):
            course_id = raw_input('Enter a course_id: ')
            instance.show_tabs(course_id)
        elif testnum == str(9):
            course_id = raw_input('Enter a course_id: ')
            tab_id = raw_input('Enter tab id: ')
            visible = raw_input('Enter visibility value (public, members, admins, and none): ')
            instance.set_tab_visibility(course_id, tab_id, visible)
        elif testnum == str(10):
            account_id = raw_input('Enter account id: ')
            instance.get_account_courses(account_id)
        elif testnum == str(11):
            course_id = '4580'
            url = '/Users/epp785/image.jpg'
            size = '51047'
            instance.upload_file(course_id, url, size)
        elif testnum == str(0):
            sys.exit(0)
        else:
            print "Not yet implemented"


if __name__ == "__main__":
    main()
