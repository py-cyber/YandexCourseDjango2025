import json

from channels.generic.websocket import AsyncWebsocketConsumer

import duels.models


class SearchPlayers(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if not user.is_authenticated:
            await self.close()

        players = duels.models.WaitingPlayers.objects.get_suitable_user(user)
        if not players.exists():
            duels.models.WaitingPlayers.objects.create(user=user)
            await self.accept()
            await self.send(text_data=json.dumps({
                'message': 'search start',
            }))
            return

        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'opponent is found',
        }))
        opponent = players[0]

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
