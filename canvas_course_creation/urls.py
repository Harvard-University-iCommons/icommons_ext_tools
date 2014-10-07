from django.conf.urls import patterns, url

from .views import CanvasCourseSiteCreateView, CanvasCourseSiteStatusView

urlpatterns = patterns(
    '',
    url(r'^(\d*)$', 'canvas_course_creation.views.index', name='index'),
    url(r'^courses/(?P<pk>\d+)/create$', CanvasCourseSiteCreateView.as_view(), name='ccsw-create'),
    url(r'^status/(?P<pk>\d+)$', CanvasCourseSiteStatusView.as_view(), name='ccsw-status'),
)
