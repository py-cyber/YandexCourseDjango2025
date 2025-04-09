import django.urls

import problems.views

app_name = 'problems'
urlpatterns = [
    django.urls.path('', problems.views.ProblemsListView.as_view(), name='all'),
    django.urls.path('/<int:pk>', problems.views.problem_view, name='problem'),
]
