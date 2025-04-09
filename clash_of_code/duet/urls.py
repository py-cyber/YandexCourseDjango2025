from django.urls import path

from duet import consumers, views


app_name = 'duet'

urlpatterns = [
    path('create/', views.CodeRoomCreateView.as_view(), name='create_room'),
    path('<int:pk>/', views.CodeRoomDetailView.as_view(), name='room_detail'),
    path('my-rooms/', views.UserRoomsListView.as_view(), name='user_rooms'),
    path('<int:pk>/save/', views.CodeRoomSaveView.as_view(), name='save_room_content'),
    path(
        '<int:room_id>/invite/',
        views.RoomInviteCreateView.as_view(),
        name='invite_user',
    ),
    path('my-invitations/', views.InvitationsListView.as_view(), name='my_invitations'),
    path(
        'invitations/<int:invitation_id>/accept/',
        views.AcceptInvitationView.as_view(),
        name='accept_invitation',
    ),
]

websocket_urlpatterns = [
    path('ws/code_room/<int:room_id>/', consumers.CodeRoomConsumer.as_asgi()),
]
