import django.http
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView

import problems.models
import problems.forms


class ProblemsListView(ListView):
    model = problems.models.Problem
    queryset = problems.models.Problem.objects.all_problem_list()
    template_name = 'problems/all_problems.html'
    paginate_by = 20


class ProblemsCreateView(LoginRequiredMixin, CreateView):
    model = problems.models.Problem
    form_class = problems.forms.ProblemsForm
    template_name = 'problems/problem_form.html'

    def form_valid(self, form: problems.forms.ProblemsForm):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('problems:update', kwargs={'pk': self.object.pk})


class ProblemsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = problems.models.Problem
    form_class = problems.forms.ProblemsForm
    template_name = 'problems/problem_form.html'

    def get_success_url(self):
        return reverse('problems:update', kwargs={'pk': self.object.pk})

    def test_func(self):
        problem = self.get_object()
        return self.request.user == problem.author


def problem_view(request, pk):
    return django.http.HttpResponse('бла бла бла')
