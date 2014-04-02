from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'icommons_ext_tools.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #url(r'^admin/', include(admin.site.urls)),

    url(r'^ext_tools/qualtrics_link/', include('qualtrics_link.urls', namespace="ql")),

    url(r'^ext_tools/canvas_wizard/', include('canvas_wizard.urls', namespace="cw")),

    url(r'^ext_tools/pin/', include('icommons_common.auth.urls', namespace="pin")),

    url(r'^ext_tools/not_authorized/', 'icommons_ui.views.not_authorized', name="not_authorized"),
)
