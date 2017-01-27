from django.conf.urls import url

from qualtrics_link import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^get_org_info\.json$', views.get_org_info, name='get_org_info'),
    url(r'^internal$', views.internal, name='internal'),
    url(r'^launch$', views.launch, name='launch'),
    url(r'^monitor$', views.MonitorResponseView.as_view()),
    url(r'^user_accept_terms$', views.user_accept_terms, name='user_accept_terms'),
    url(r'^user_decline_terms$', views.user_decline_terms, name='user_decline_terms'),
]
