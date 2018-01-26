import django_cas_ng
from django.conf import settings
from django.conf.urls import url, include

from icommons_ui import views as ui_views
from qualtrics_link import urls as ql_urls

urlpatterns = [
    url(r'^accounts/login/', django_cas_ng.views.login, name='cas_ng_login'),
    url(r'^accounts/logout/', django_cas_ng.views.logout, name='cas_ng_logout'),
    url(r'^ext_tools/not_authorized/', ui_views.not_authorized, name="not_authorized"),
    url(r'^ext_tools/qualtrics_link/', include(ql_urls, namespace="ql")),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

handler403 = 'icommons_ext_tools.views.handler403'
handler404 = 'icommons_ext_tools.views.handler404'
handler500 = 'icommons_ext_tools.views.handler500'
