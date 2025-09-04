from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from . import views
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from .views import health_check # Import the new view

urlpatterns = [
    # Health Check
    path('api/health/', views.health_check, name='health_check'),
    path('api/data/', views.api_data, name='api_data'),

    # Admin
    path('admin/', admin.site.urls),

    # Public API endpoints (auth, etc.)
    path('', include('urls_public')),

    # API endpoints
    path('api/users/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),

    # API Schema (Swagger/Redoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
