# backend/apps/chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from agents.applaude_prime_agent import ApplaudePrimeAgent
from apps.projects.tasks import send_project_status_notification
from apps.projects.models import Project

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name  # Use room_name directly as group name

        # User authentication via token in query string
        token_key = self.scope['query_string'].decode().split('=')[1]
        self.user = await self.get_user(token_key)

        if self.user.is_anonymous:
            await self.close()
            return

        # Initialize the Applaude Prime agent
        self.agent = ApplaudePrimeAgent()
        self.current_project_id = None

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Announce user connection
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{self.user.username} has joined the chat.",
                'sender': 'system'
            }
        )

    async def disconnect(self, close_code):
        # Announce user disconnection
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{self.user.username} has left the chat.",
                'sender': 'system'
            }
        )
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username
            }
        )

        # Get response from Applaude Prime agent
        ai_response, self.current_project_id = await self.get_ai_response(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': ai_response,
                'sender': 'Applaude Prime'
            }
        )

        # Send project status update if we have a project
        if self.current_project_id:
            await self.send_project_status_update()

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @database_sync_to_async
    def get_user(self, token_key):
        try:
            # Decode the JWT token
            access_token = AccessToken(token_key)
            user_id = access_token.payload.get('user_id')
            if user_id:
                User = get_user_model()
                return User.objects.get(id=user_id)
            else:
                return AnonymousUser()
        except Exception:
            return AnonymousUser()

    @database_sync_to_async
    def get_ai_response(self, user_message):
        # Call the agent's execute method
        response, project_id = self.agent.execute(user_message, self.current_project_id, self.user)
        return response, project_id

    async def send_project_status_update(self):
        """Send current project status to the frontend"""
        if not self.current_project_id:
            return
            
        project = await self.get_project(self.current_project_id)
        if project:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'project_status_update',
                    'project_id': str(project.id),
                    'status': project.status,
                    'status_message': project.status_message,
                    'progress': self.get_progress_percentage(project.status),
                    'project_data': {
                        'name': project.name,
                        'source_url': project.source_url,
                        'user_persona_document': project.user_persona_document,
                        'brand_palette': project.brand_palette,
                        'generated_code_path': project.generated_code_path,
                    }
                }
            )

    @database_sync_to_async
    def get_project(self, project_id):
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None

    def get_progress_percentage(self, status):
        """Convert project status to progress percentage"""
        status_progress = {
            'PENDING': 0,
            'ANALYSIS_PENDING': 10,
            'ANALYSIS_COMPLETE': 20,
            'DESIGN_PENDING': 30,
            'DESIGN_COMPLETE': 40,
            'CODE_GENERATION': 50,
            'QA_PENDING': 60,
            'QA_COMPLETE': 70,
            'DEPLOYMENT_PENDING': 80,
            'COMPLETED': 100,
            'FAILED': 0,
        }
        return status_progress.get(status, 0)

    async def project_status_update(self, event):
        """Handle project status updates from other parts of the system"""
        await self.send(text_data=json.dumps({
            'type': 'project_status_update',
            'project_id': event['project_id'],
            'status': event['status'],
            'status_message': event['status_message'],
            'progress': event['progress'],
            'project_data': event['project_data']
        }))

    async def task_started(self, event):
        """Handle task start notifications"""
        await self.send(text_data=json.dumps({
            'type': 'task_started',
            'project_id': event['project_id'],
            'task_name': event['task_name'],
            'task_description': event['task_description']
        }))

    async def task_completed(self, event):
        """Handle task completion notifications"""
        await self.send(text_data=json.dumps({
            'type': 'task_completed',
            'project_id': event['project_id'],
            'task_name': event['task_name'],
            'task_result': event['task_result']
        }))