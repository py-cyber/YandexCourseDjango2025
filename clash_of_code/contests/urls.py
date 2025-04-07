from django.urls import path

from contests import views


app_name = 'contests'


urlpatterns = [
    path(
        'create/',
        views.ContestCreateView.as_view(),
        name='create',
    ),
]
