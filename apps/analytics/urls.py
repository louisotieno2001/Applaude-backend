from django.urls import path
from .views import AppAnalyticsView

app_name = 'analytics'

urlpatterns = [
    path('<int:project_id>/', AppAnalyticsView.as_view(), name='project-analytics'),
]
