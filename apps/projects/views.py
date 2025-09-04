from rest_framework import viewsets, permissions
from .models import Project
from apps.testimonials.models import Testimonial
from .serializers import ProjectSerializer, TestimonialSerializer
from django_ratelimit.decorators import ratelimit

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to interact with it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the project.
        return obj.owner == request.user

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    Ensures that users can only interact with their own projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_permissions(self):
        """
        Allow unauthenticated users to list projects (returns empty list),
        but require authentication for other operations.
        """
        if self.action == 'list':
            return []
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


    def get_queryset(self):
        """
        This view should return a list of all the projects
        for the currently authenticated user, prefetching related apps
        to optimize database queries.
        If user is not authenticated, return empty queryset.
        """
        if self.request.user.is_authenticated:
            user = self.request.user
            return Project.objects.filter(owner=user).prefetch_related('testimonials')
        return Project.objects.none()

    def perform_create(self, serializer):
        """
        Assign the current user as the owner of the project upon creation.
        """
        serializer.save(owner=self.request.user)


class TestimonialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for testimonials. For this launch, it is read-only.
    """
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return testimonials for projects owned by the current user.
        """
        user = self.request.user
        return Testimonial.objects.filter(project__owner=user).select_related('project')



