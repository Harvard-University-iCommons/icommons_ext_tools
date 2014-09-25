from django.conf.urls import patterns, url

from .views import CourseView

urlpatterns = patterns(
    '',
    url(r'^courses/$', CourseView.as_view(), name='ccc-courses'),
)
