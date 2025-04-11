import django.urls

import problems.views

app_name = 'problems'
urlpatterns = [
    django.urls.path('', problems.views.ProblemsListView.as_view(), name='all'),
    django.urls.path(
        'create/',
        problems.views.ProblemsCreateView.as_view(),
        name='create_task',
    ),
    django.urls.path(
        'update/<int:pk>/',
        problems.views.ProblemsUpdateView.as_view(),
        name='update',
    ),
    django.urls.path(
        'tests/<int:pk>/',
        problems.views.ProblemsTestView.as_view(),
        name='tests',
    ),
    django.urls.path('<int:pk>/', problems.views.problem_view, name='problem'),
    django.urls.path(
        'delete_test/<int:pk>/',
        problems.views.DeleteTestView.as_view(),
        name='delete_test',
    ),
    django.urls.path(
        'tests/<int:pk>/update-task-order/',
        problems.views.UpdateTestOrderView.as_view(),
        name='update_task_order',
    ),
]
