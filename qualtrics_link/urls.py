from django.conf.urls import patterns, url

from .views import MonitorResponseView

urlpatterns = patterns('',

    url(r'^$', 'qualtrics_link.views.index', name='index'),

    url(r'^launch$', 'qualtrics_link.views.launch', name='launch'),

    url(r'^internal$', 'qualtrics_link.views.internal', name='launch'),

    url(r'^get_org_info$', 'qualtrics_link.views.get_org_info', name='get_org_info'),

    url(r'^user_accept_terms$', 'qualtrics_link.views.user_accept_terms', name='user_accept_terms'),

    url(r'^user_decline_terms$', 'qualtrics_link.views.user_decline_terms', name='user_decline_terms'),

    url(r'^monitor$', MonitorResponseView.as_view()),
    
)

