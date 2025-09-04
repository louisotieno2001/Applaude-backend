from django.urls import path
from .views import (
    SubmitSurveyResponseView, 
    SubmitAppRatingView, 
    SubmitUserFeedbackView,
    ProjectAnalyticsView
)

app_name = 'surveys'

urlpatterns = [
    path('submit/survey/', SubmitSurveyResponseView.as_view(), name='submit-survey'),
    path('submit/rating/', SubmitAppRatingView.as_view(), name='submit-rating'),
    path('submit/feedback/', SubmitUserFeedbackView.as_view(), name='submit-feedback'),
    path('analytics/<int:pk>/', ProjectAnalyticsView.as_view(), name='project-analytics'),
]
