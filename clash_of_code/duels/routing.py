from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/some_path/', consumers.SearchPlayers.as_asgi()),
]

