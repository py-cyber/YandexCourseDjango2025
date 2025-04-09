import django.http
from django.views.generic import ListView

import problems.models


class ProblemsListView(ListView):
    model = problems.models.Problem
    queryset = problems.models.Problem.objects.all_problem_list()
    template_name = 'problems/all_problems.html'
    paginate_by = 20


def problem_view(request, pk):
    return django.http.HttpResponse('бла бла бла')
