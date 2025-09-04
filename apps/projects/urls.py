from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('new/', ProjectViewSet.as_view({'post': 'create'}), name='project-create'),
    path('', include(router.urls)),
]
