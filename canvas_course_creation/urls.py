from django.conf.urls import patterns, url

from .views import CourseView

urlpatterns = patterns(
    '',
    url(r'^$', 'canvas_course_creation.views.index', name='index'),
    url(r'^courses/$', CourseView.as_view(), name='ccc-courses'),
)
