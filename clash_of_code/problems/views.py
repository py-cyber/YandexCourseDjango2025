from django.views.generic import ListView

import problems.models


class ProblemsListView(ListView):
    model = problems.models.Problem

