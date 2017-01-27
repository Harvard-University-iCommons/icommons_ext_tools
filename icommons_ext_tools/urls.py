from django.conf.urls import (
    include,
    url)
from icommons_ui import views as ui_views
from qualtrics_link import urls as ql_urls

urlpatterns = [
    url(r'^ext_tools/not_authorized/', ui_views.not_authorized, name="not_authorized"),
    url(r'^ext_tools/pin/', include('icommons_common.auth.urls', namespace="pin")),
    url(r'^ext_tools/qualtrics_link/', include(ql_urls, namespace="ql")),
]

handler403 = 'icommons_ext_tools.views.handler403'
handler404 = 'icommons_ext_tools.views.handler404'
handler500 = 'icommons_ext_tools.views.handler500'
