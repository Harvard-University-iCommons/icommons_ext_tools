from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from icommons_common.monitor.views import BaseMonitorResponseView
from icommons_common.models import School, CourseInstance, Template, TemplateAccessList, TemplateUser, TemplateAccount
from icommons_common.canvas_utils import *
from icommons_common.icommonsapi import IcommonsApi
from icommons_common.auth.decorators import group_membership_restriction

from canvas_wizard.forms import AddTemplateForm, AddUserForm

from django.http import HttpResponse
from datetime import date
import time
import json
import datetime
import urllib
import pprint

from canvas_api import Canvasapi

logger = logging.getLogger(__name__)

class MonitorResponseView(BaseMonitorResponseView):
    def healthy(self):
        return True

@login_required
@require_http_methods(['GET'])
def index(request):
    """
    doc string
    """
    return render(request, 'canvas_wizard/index.html')

@login_required
@require_http_methods(['GET'])
def launch(request):
    """
    doc string
    """
    huid = request.user.username
    request.session['huid'] = huid
    templateuser = TemplateUser.objects.get(user_id=huid)    
    sis_id = templateuser.sis_account_id
    can_manage_templates = templateuser.can_manage_templates
    can_bulk_create_courses = templateuser.can_bulk_create_courses
    can_manage_users = templateuser.can_manage_users
    templateaccount = TemplateAccount.objects.get(sis_account_id=sis_id)
    can_use_wizard = templateaccount.can_use_wizard
    request.session['can_use_wizard'] = can_use_wizard
    request.session['sis_id'] = sis_id

    return render(request, 'canvas_wizard/launch.html', {'huid': huid, \
        'can_use_wizard' : can_use_wizard, \
        'can_manage_templates' : can_manage_templates, \
        'can_bulk_create_courses' : can_bulk_create_courses, \
        'can_manage_users' : can_manage_users, \
        })

@login_required
@require_http_methods(['GET'])
def select_course(request):
    """
    doc string
    """

    userdata = {}

    if 'huid' in request.GET:
        logger.info('We are spoofing!!!')
        huid = request.GET['huid']
        userdata['spoofing'] = True
        huid = huid.strip()
    else:
        huid = request.session['huid']

    persondataobj = IcommonsApi()
    resp = persondataobj.people_by_id(huid)
    persondata = resp.json()
    if 'people' in persondata:
        person = persondata['people'][0]
        userdata['firstname'] = person.get('firstName', 'Not Available')
        userdata['lastname'] = person.get('lastName', 'Not Available')
        userdata['email'] = person.get('email', 'Not Available')
        userdata['huid'] = huid

    if 'course_id' in request.session:
        del request.session['course_id']

    if 'template_id' in request.session:
        del request.session['template_id']
    
    if 'isite_site_id' in request.session:
        del request.session['isite_site_id']

    if 'courses' in request.session:
        del request.session['courses']

    course_instances = CourseInstance.objects.filter(course_staff__user_id=huid, course_staff__role_id=2).order_by('-course_instance_id')
    # sync_to_canvas=1 We may need to set this if it's not already set

    return render(request, 'canvas_wizard/select_course.html', {'courses' : course_instances, 'userdata' : userdata})

'''
@login_required
@require_http_methods(['GET'])
def select_template_or_course(request):
    """
    doc string
    """

    course_instances = CourseInstance.objects.filter(course_staff__user_id=request.session['huid'], \
        course_staff__role_id=2).order_by('-course_instance_id')
    templateaccesslist = Template.objects.filter(template_obj__templateuser__template_user_id=request.session['huid'])
    course_instances = CourseInstance.objects.filter(course_staff__user_id=request.session['huid'], \
        course_staff__role_id=2, canvas_course_id__gt=0).order_by('-course_instance_id')

    if 'course' in request.GET:
        course_id = request.GET['course']
        request.session['course_id'] = course_id
        selected_course = CourseInstance.objects.get(course_instance_id=course_id)

        selected_course_dict = {
            'course_instance_id' :selected_course.course_instance_id,
            'term' : selected_course.term.school.title_short + " / " + selected_course.term.display_name,
            'short_title' : selected_course.short_title,
            'title' : selected_course.title,
        }

        request.session['selected_course'] = selected_course_dict
    else:
        logger.error('No course selected!')
        return redirect('select_course')
    
    return render(request, 'canvas_wizard/select_template_or_course.html', \
        {'session' : request.session, 'selected_course' : selected_course_dict, \
        'courses' : course_instances, 'templates' : templateaccesslist})
'''

@login_required
@require_http_methods(['GET'])
def course_setup(request, school, registrar_code, year, term):
    """
    Display course info from url. This view is accessed by url in the form 
    select_course/school/registrar_code/year/term
    If the user is in the staff list of the course, they will get an option to
    create the canvas course. 
    """
    
    msg = None
    selected_course_dict = None
    user_can_create_course = False
    selected_course = None
    can_use_wizard = None
    course_instances = None
    templateaccesslist = None
    huid = request.session['huid']
   
    templateaccesslist = Template.objects.filter(template_access__templateuser__user_id=huid)
    course_instances = CourseInstance.objects.filter(\
            course_staff__user_id=huid, \
            course_staff__role_id=2, \
            canvas_course_id__gt=0).order_by('-course_instance_id' \
            )

    try:
        selected_course = CourseInstance.objects.get(\
            course__registrar_code=registrar_code, \
            term__school_id=school, \
            term__academic_year=year, \
            term__term_code__term_name__startswith=term \
            )

        selected_course_dict = {
            'course_instance_id' :selected_course.course_instance_id,
            'term' : selected_course.term.school.title_short + " / " + selected_course.term.display_name,
            'short_title' : selected_course.short_title,
            'title' : selected_course.title,
            'location' : selected_course.location,
            'meeting_time' : selected_course.meeting_time,
            'instructors_display' : selected_course.instructors_display,
            'description' : selected_course.description,
            'notes' : selected_course.notes,
        }
        request.session['selected_course'] = selected_course_dict
    except CourseInstance.DoesNotExist:
        msg = 'Course Not Found'
    
    # check to see if the user is course staff, if so, they can create the course
    required_group = 'ScaleCourseStaff:%s' % selected_course.course_instance_id
    print required_group
    group_ids = request.session.get('USER_GROUPS', [])
    if required_group in group_ids:
        user_can_create_course = True
    
    #TODO - Add check to see if the user is a delegate of the course

    return render(request, 'canvas_wizard/course_setup.html', \
        {
        'admin' : user_can_create_course, \
        'session' : request.session, \
        'selected_course' : selected_course_dict, \
        'courses' : course_instances, \
        'templates' : templateaccesslist, \
        'msg' : msg, \
        'can_use_wizard' : can_use_wizard, \
        })


@login_required
@require_http_methods(['GET'])
def select_isite_import(request):
    """
    doc string
    """
    template_id = None
    selected_course = None
    selected_template = None
    selected_template_dict = None
    
    if 'template' in request.GET:
        template_id_input = request.GET['template']
        request.session['template_id_input'] = template_id_input
        if 'course' in template_id_input:
            template_id = template_id_input.split('-')[1]
            selected_template = CourseInstance.objects.get(canvas_course_id=template_id)
            selected_template_dict = {
                'template_id' : selected_template.course_instance_id,\
                'term' : selected_template.term.display_name,\
                'title' : selected_template.title,\
                'type' : 'course',\
            }
        elif 'template' in template_id_input:
            template_id = template_id_input.split('-')[1]
            selected_template = Template.objects.filter(template_id=template_id)
            selected_template_dict = {
                'template_id' : selected_template.template_id,\
                'term' : selected_template.template_term,\
                'title' : selected_template.template_title,\
                'type' : 'template',\
            }
        else:
            logger.error('An error has occured, template_id does not contain "course" or "template"')
        
        #request.session['template_id'] = template_id

    selected_course = request.session['selected_course']
    request.session['selected_template_dict'] = selected_template_dict

    return render(request, 'canvas_wizard/select_isite_import.html', \
        { \
        'session' : request.session, \
        'selected_course' : selected_course, \
        'selected_template' : selected_template_dict, \
        })

@login_required
@require_http_methods(['GET'])
def finish(request):
    """
    doc string
    """
    if 'isite_site_id' in request.GET:
        isite_site_id = request.GET['isite_site_id']
        request.session['isite_site_id'] = isite_site_id

    # here we will initiate the course copy and isites import
    # instance.create_course_content_migration(source_course_id, course_id)
    return render(request, 'canvas_wizard/finish.html', {'session' : request.session})

@login_required
@require_http_methods(['GET'])
def manage_templates(request):
    """
    doc string
    """
    templates = Template.objects.filter(template_access__templateuser__user_id=request.session['huid'])
    return render(request, 'canvas_wizard/manage_templates.html', \
        {\
        'session' : request.session, \
        'templates' : templates, \
        })

@login_required
#@require_http_methods(['GET'])
def add_new_template_form(request):
    """
    doc string
    """
    form = AddTemplateForm()
    return render(request, 'canvas_wizard/add_new_template_form.html', \
        {\
        'request': request, \
        'form': form, \
        })

@login_required
@require_http_methods(['POST'])
def add_new_template_action(request):
    """
    doc string
    """
    from django.db import connection, transaction
    logger.debug('in add_new_template_action')
    cursor = connection.cursor()
    cursor.execute('SELECT TEMPLATES_SQ.NEXTVAL FROM DUAL')
    row = cursor.fetchone()
    template_id = row[0]
    cursor.execute('SELECT TEMPLATES_ACCESS_SQ.NEXTVAL FROM DUAL')
    row = cursor.fetchone()
    access_id = row[0]
    sis_id = request.session['sis_id']
    form = AddTemplateForm(data=request.POST, template_id=template_id)
    if form.is_valid():
        form.save()
        today = datetime.datetime.now()
        sql = "INSERT INTO TEMPLATE_ACCESS_LIST VALUES('%s', %i, '%s','%s',%i)" % (sis_id, template_id, request.session['huid'], today, access_id)
        cursor.execute(sql)
        transaction.commit()

    templates = Template.objects.filter(template_access__templateuser__user_id=request.session['huid'])

    return render(request, 'canvas_wizard/manage_templates.html', \
        {\
        'request': request, \
        'templates' : templates, \
        })

@login_required
@require_http_methods(['GET'])
def delete_template(request):
    """
    doc string
    """
    
    # get templates

    #return render(request, 'canvas_wizard/delete_template.html', {'session' : request.session})
    result = '{}'
    response = HttpResponse(result, content_type="application/json")
    response["Access-Control-Allow-Origin"] = "*" 
    return response

@login_required
@require_http_methods(['GET'])
def manage_users(request):
    """
    doc string
    """
    users = TemplateUser.objects.all()

    #return render(request, 'canvas_wizard/delete_template.html', {'session' : request.session})
    return render(request, 'canvas_wizard/manage_users.html', \
        {\
        'request': request, \
        'users' : users, \
        })

@login_required
@require_http_methods(['GET'])
def add_new_user_form(request):
    """
    doc string
    """
    form = AddUserForm()

    #return render(request, 'canvas_wizard/delete_template.html', {'session' : request.session})
    return render(request, 'canvas_wizard/add_new_user_form.html', \
        {\
        'request': request, \
        'form' : form, \
        })

@login_required
@require_http_methods(['POST'])
def add_new_user_action(request):
    """
    doc string
    """
    form = AddUserForm(data=request.POST)
    if form.is_valid:
        form.save()

    users = TemplateUser.objects.all()

    #return render(request, 'canvas_wizard/delete_template.html', {'session' : request.session})
    return render(request, 'canvas_wizard/manage_users.html', \
        {\
        'request': request, \
        'users' : users, \
        'form' : form, \
        })





