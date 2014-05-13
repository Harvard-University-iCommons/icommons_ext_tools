from django.conf.urls import patterns, url

from .views import CourseWizardIndexView, CourseCatalogIndexView

urlpatterns = patterns(
    '',
    url(r'^$', CourseWizardIndexView.as_view(), name='wizard-index'),
    url(r'^catalog/(?P<school>\w+)/(?P<registrar_code>[-\w]+)/(?P<year>\d{4})/(?P<term>\w+)$',
        CourseCatalogIndexView.as_view(), name='course-catalog'),
)
