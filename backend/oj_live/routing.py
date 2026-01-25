from django.urls import re_path

from .consumers import LiveSessionConsumer

websocket_urlpatterns = [
    re_path(r'ws/live/(?P<session_id>\d+)/$', LiveSessionConsumer.as_asgi()),
]
