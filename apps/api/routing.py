from django.urls import re_path
from apps.projects import consumers
from apps.chat import consumers as chat_consumers

websocket_urlpatterns = [
    re_path(r'ws/project/(?P<project_id>\w+)/$', consumers.ProjectStatusConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', chat_consumers.ChatConsumer.as_asgi()),
]
