from django.urls import re_path
from apps.projects import consumers

websocket_urlpatterns = [
    re_path(r'ws/project/(?P<project_id>\w+)/$', consumers.ProjectStatusConsumer.as_asgi()),
]
