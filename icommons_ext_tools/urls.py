from django.conf import settings
from django.urls import path, re_path, include
import django_cas_ng.views as cas_ng_views

from icommons_ui import views as ui_views

urlpatterns = [
    path('accounts/login/', cas_ng_views.LoginView.as_view(), name='cas_ng_login'),
    path('accounts/logout/', cas_ng_views.LogoutView.as_view(), name='cas_ng_logout'),
    path('ext_tools/not_authorized/', ui_views.not_authorized, name="not_authorized"),
    path('ext_tools/qualtrics_link/', include('qualtrics_link.urls', namespace='ql')),
]

if settings.DEBUG:
    try:
        import debug_toolbar
        urlpatterns += [
            re_path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass  # This is OK for a deployed instance running in DEBUG mode

handler403 = 'icommons_ext_tools.views.handler403'
handler404 = 'icommons_ext_tools.views.handler404'
handler500 = 'icommons_ext_tools.views.handler500'
