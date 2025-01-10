from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

from starpal import settings

api_version = 'api/v1/'
api_patterns = [
    path(api_version + 'users/', include('appuser.urls')),
    path(api_version + 'services/', include('service.urls')),
    path(api_version + 'celebservices/', include('celebservice.urls')),
    path(api_version + 'requests/', include('request.urls')),
    path(api_version + 'mpesainvoices/', include('mpesainvoices.urls')),
    path('accounts/', include('allauth.urls')),
    path('childsafety/', include('appuser.urls')),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path('', include('web.urls')),
]

urlpatterns = api_patterns

# urlpatterns = api_patterns + [
#     path('admin/', admin.site.urls),
# ]

if settings.DEBUG:
    adminurl = [
        path('admin/', admin.site.urls),
    ]
    urlpatterns += adminurl

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
