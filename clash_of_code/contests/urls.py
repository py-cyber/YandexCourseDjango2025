from django.urls import path

from contests import views


app_name = 'contests'


urlpatterns = [
    path(
        'create/',
        views.ContestCreateView.as_view(),
        name='create',
    ),
    path(
        '<int:pk>/',
        views.ContestDetailView.as_view(),
        name='detail',
    ),
    path(
        '<int:pk>/register/',
        views.ContestRegisterView.as_view(),
        name='register',
    ),
    path(
        '<int:pk>/standings/',
        views.ContestStandingsView.as_view(),
        name='standings',
    ),
]
