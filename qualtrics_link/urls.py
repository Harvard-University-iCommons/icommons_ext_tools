from django.urls import path, re_path

from qualtrics_link import views

app_name = 'ql'
urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^get_org_info\.json$', views.get_org_info, name='get_org_info'),
    path('internal', views.internal, name='internal'),
    re_path(r'^launch$', views.launch, name='launch'),
    re_path(r'^monitor$', views.MonitorResponseView.as_view()),
    re_path(r'^user_accept_terms$', views.user_accept_terms, name='user_accept_terms'),
    re_path(r'^user_decline_terms$', views.user_decline_terms, name='user_decline_terms'),
]
