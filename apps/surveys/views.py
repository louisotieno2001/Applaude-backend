from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import SurveyResponse, AppRating, UserFeedback
from .serializers import SurveyResponseSerializer, AppRatingSerializer, UserFeedbackSerializer
from apps.projects.models import Project
from agents.tasks import process_feedback_data

class SubmitSurveyResponseView(generics.CreateAPIView):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        # Trigger async task to process this new feedback
        process_feedback_data.delay(project_id)
        serializer.save()

class SubmitAppRatingView(generics.CreateAPIView):
    queryset = AppRating.objects.all()
    serializer_class = AppRatingSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        process_feedback_data.delay(project_id)
        serializer.save()

class SubmitUserFeedbackView(generics.CreateAPIView):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        process_feedback_data.delay(project_id)
        serializer.save()

class ProjectAnalyticsView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        project = self.get_object()
        if project.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
            
        analytics_data = {
            'app_ratings_summary': project.app_ratings_summary,
            'user_feedback_summary': project.user_feedback_summary,
            'survey_response_analytics': project.survey_response_analytics,
        }
        return Response(analytics_data)
