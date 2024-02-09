"""
URL configuration for webapp project.
"""

from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from . import views
from . import settings


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace="users")),
    path('library/', include('library.urls', namespace="library")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
