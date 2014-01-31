from django.conf.urls import patterns, url



urlpatterns = patterns('',

    url(r'^$', 'qualtrics_link.views.index', name='index'),

    url(r'^launch$', 'qualtrics_link.views.launch', name='launch'),

    url(r'^main$', 'qualtrics_link.views.main', name='main'),

    
)

