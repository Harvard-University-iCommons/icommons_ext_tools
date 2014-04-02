from django.conf.urls import patterns, url

from .views import MonitorResponseView

urlpatterns = patterns('',

    url(r'^$', 'canvas_wizard.views.index', name='index'),

    url(r'^launch$', 'canvas_wizard.views.launch', name='launch'),

    url(r'^select_course$', 'canvas_wizard.views.select_course', name='select_course'),

    url(r'^select_template_or_course$', 'canvas_wizard.views.select_template_or_course', name='select_template_or_course'),

    url(r'^select_isite_import$', 'canvas_wizard.views.select_isite_import', name='select_isite_import'),

    url(r'^finish$', 'canvas_wizard.views.finish', name='finish'),

    url(r'^monitor$', MonitorResponseView.as_view()),
    
)

