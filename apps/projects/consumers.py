import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ProjectStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_group_name = f'project_{self.project_id}'

        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.project_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.project_group_name,
            {
                'type': 'project_update',
                'message': message
            }
        )

    async def project_update(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
