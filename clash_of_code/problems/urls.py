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
    django.urls.path(
        'my_tasks/',
        problems.views.AllMyTaskView.as_view(),
        name='my_tasks',
    ),
    django.urls.path(
        '<int:pk>/',
        problems.views.ProblemDetailView.as_view(),
        name='problem',
    ),
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
    django.urls.path(
        'check_author_solution/<int:pk>/',
        problems.views.CheckAuthorSolutionView.as_view(),
        name='check_author_solution',
    ),
    django.urls.path(
        'submit/<int:pk>/',
        problems.views.SubmitSolutionView.as_view(),
        name='submit_solution',
    ),
    django.urls.path(
        'submissions/<int:pk>/',
        problems.views.MySubmissionsView.as_view(),
        name='my_submissions',
    ),
    django.urls.path(
        'submission/<int:pk>/',
        problems.views.SubmissionDetailView.as_view(),
        name='submission_detail',
    ),
]
