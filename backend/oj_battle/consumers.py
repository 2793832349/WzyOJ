from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import BattleRoom


class BattleRoomConsumer(AsyncJsonWebsocketConsumer):
    room_id = None
    group_name = None

    @database_sync_to_async
    def _get_room(self, room_id):
        return BattleRoom.objects.filter(id=room_id).first()

    @database_sync_to_async
    def _is_participant(self, room, user_id):
        return room.participants.filter(user_id=user_id).exists()

    async def connect(self):
        user = self.scope.get('user')
        if not user or not getattr(user, 'is_authenticated', False):
            await self.close(code=4401)
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f'battle_room_{self.room_id}'

        room = await self._get_room(self.room_id)
        if not room:
            await self.close(code=4404)
            return

        is_participant = await self._is_participant(room, user.id)
        if not is_participant and not user.is_staff:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if self.group_name:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        return

    async def battle_event(self, event):
        await self.send_json(event.get('payload', {}))
