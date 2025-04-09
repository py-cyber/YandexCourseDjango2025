import django.urls

import problems.views

app_name = 'problems'
urlpatterns = [
    django.urls.path('', problems.views.ProblemsListView.as_view(), name='all'),
    django.urls.path(
        'create/', problems.views.ProblemsCreateView.as_view(), name='create_task'
    ),
    django.urls.path(
        'update/<int:pk>', problems.views.ProblemsUpdateView.as_view(), name='update'
    ),
    django.urls.path('/<int:pk>', problems.views.problem_view, name='problem'),
]
