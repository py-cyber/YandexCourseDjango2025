import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from duet.models import CodeRoom


class CodeRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'code_room_{self.room_id}'

        user = self.scope['user']
        if not await self.check_access(user):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        room = await self.get_room()
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'room_state',
                    'content': room.content,
                    'language': room.language.ace_mode,
                },
            ),
        )

    async def disconnect(self):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'code_update':
            content = text_data_json['content']
            user = self.scope['user']

            await self.update_room_content(content)

            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'code_update', 'content': content, 'sender': user.username},
            )

    async def code_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    'type': 'code_update',
                    'content': event['content'],
                    'sender': event['sender'],
                },
            ),
        )

    @database_sync_to_async
    def check_access(self, user):
        return CodeRoom.objects.filter(id=self.room_id, participants=user).exists()

    @database_sync_to_async
    def get_room(self):
        return CodeRoom.objects.get(id=self.room_id)

    @database_sync_to_async
    def update_room_content(self, content):
        CodeRoom.objects.filter(id=self.room_id).update(content=content)
