from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Tenant-specific Admin
    path('admin/', admin.site.urls),

    # Tenant-specific APIs
    path('api/', include('apps.projects.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.api.urls')),

    # Note: User management is largely handled in the public schema,
    # but you could have tenant-specific user profile endpoints here if needed.
]
