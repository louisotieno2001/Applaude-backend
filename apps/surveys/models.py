from django.db import models
from django.conf import settings
from apps.projects.models import Project
import uuid

class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='survey_responses')
    user_identifier = models.CharField(max_length=255) # Could be a device ID or a user ID if logged in
    survey_type = models.CharField(max_length=50) # e.g., 'UX', 'PMF'
    responses = models.JSONField() # {'question_id': 'answer'}
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response for {self.project.name} ({self.survey_type}) at {self.created_at}"

class AppRating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='app_ratings')
    user_identifier = models.CharField(max_length=255)
    rating = models.IntegerField() # 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}-star rating for {self.project.name}"

class UserFeedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='user_feedback')
    user_identifier = models.CharField(max_length=255)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.project.name}"
