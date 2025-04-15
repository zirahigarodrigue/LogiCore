from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from .views import home, page_not_found


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    # 
    path('api/users/', include('apps.user.urls')),
    # 
    path('api/schema/file', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
if not settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# Set the custom 404 handler
handler404 = page_not_found
if settings.DEBUG:
    handler404 = page_not_found


# Configure Admin Title
admin.site.site_header = "LogiCore API | Admin"
admin.site.index_title = "Management"