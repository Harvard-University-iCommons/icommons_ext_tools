from django.conf.urls import patterns, url



urlpatterns = patterns('',

    url(r'^$', 'qualtrics_link.views.index', name='index'),

    url(r'^launch$', 'qualtrics_link.views.launch', name='launch'),

    url(r'^org_info$', 'qualtrics_link.views.org_info', name='org_info'),

    
)

