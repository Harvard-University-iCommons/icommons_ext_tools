from django.conf.urls import patterns, url

from .views import MonitorResponseView

urlpatterns = patterns('',

    url(r'^$', 'canvas_wizard.views.index', name='index'),

    url(r'^launch$', 'canvas_wizard.views.launch', name='launch'),

    url(r'^select_course$', 'canvas_wizard.views.select_course', name='select_course'),

    url(r'^course_setup/(?P<school>\w+)/(?P<registrar_code>[-\w]+)/(?P<year>\d{,4})/(?P<term>\w+)$', \
        'canvas_wizard.views.course_setup', \
        name='course_setup'),

    url(r'^select_isite_import$', 'canvas_wizard.views.select_isite_import', \
        name='select_isite_import'),

    url(r'^manage_templates$', 'canvas_wizard.views.manage_templates', name='manage_templates'),

	url(r'^add_new_template_form$', 'canvas_wizard.views.add_new_template_form', \
        name='add_new_template_form'),
    
    url(r'^add_new_template_action$', 'canvas_wizard.views.add_new_template_action', \
        name='add_new_template_action'),
	
    url(r'^delete_template$', 'canvas_wizard.views.delete_template', name='delete_template'),

    url(r'^manage_users$', 'canvas_wizard.views.manage_users', name='manage_users'),

    url(r'^add_new_user_form$', 'canvas_wizard.views.add_new_user_form', name='add_new_user_form'),

    url(r'^add_course_delegate_form$', 'canvas_wizard.views.add_course_delegate_form', name='add_course_delegate_form'),
    url(r'^add_course_delegate_action$', 'canvas_wizard.views.add_course_delegate_action', name='add_course_delegate_action'),

    url(r'^add_new_user_action$', 'canvas_wizard.views.add_new_user_action', name='add_new_user_action'),

    url(r'^finish$', 'canvas_wizard.views.finish', name='finish'),

    url(r'^monitor$', MonitorResponseView.as_view()),
    
)

