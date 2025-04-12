from django.urls import re_path

from duet import consumers


websocket_urlpatterns = [
    re_path(r'ws/code_room/(?P<room_id>\w+)/$', consumers.CodeRoomConsumer.as_asgi()),
]
