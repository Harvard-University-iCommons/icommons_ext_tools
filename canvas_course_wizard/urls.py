from django.conf.urls import patterns, url

from .views import CourseWizardIndexView, CourseIndexView

urlpatterns = patterns(
    '',
    url(r'^$', CourseWizardIndexView.as_view(), name='wizard-index'),
    url(r'^courses/(?P<pk>\d+)/$', CourseIndexView.as_view(), name='course-index'),
)
