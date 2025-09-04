from rest_framework import generics, permissions
from .models import AppAnalytics
from .serializers import AppAnalyticsSerializer

class AppAnalyticsView(generics.ListAPIView):
    serializer_class = AppAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return AppAnalytics.objects.filter(project_id=project_id, project__owner=self.request.user)
