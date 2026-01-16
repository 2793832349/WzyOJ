from django.urls import re_path

from .consumers import BattleRoomConsumer

websocket_urlpatterns = [
    re_path(r'ws/battle/(?P<room_id>[0-9a-fA-F-]+)/$', BattleRoomConsumer.as_asgi()),
]
