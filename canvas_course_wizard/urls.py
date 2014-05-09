from django.conf.urls import patterns, url

from .views import CourseWizardIndexView

urlpatterns = patterns(
    '',
    url(r'^$', CourseWizardIndexView.as_view(), name='wizard-index'),
)
