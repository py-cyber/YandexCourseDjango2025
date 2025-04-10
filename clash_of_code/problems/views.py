import json

import django.db.transaction
import django.http
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import django.shortcuts
from django.http import HttpResponse
from django.urls import reverse
from django.views import View
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


class ProblemsTestView(LoginRequiredMixin, View):
    def get(self, request, pk):
        problem = django.shortcuts.get_object_or_404(problems.models.Problem, pk=pk)
        if problem.author != request.user:
            return django.http.HttpResponseForbidden

        context = {
            'tests': problem.tests,
            'object': problem,
        }
        return django.shortcuts.render(
            request,
            'problems/problem_add_test.html',
            context,
        )


def update_test_order(request, pk):
    problem = django.shortcuts.get_object_or_404(problems.models.Problem, pk=pk)
    if problem.author != request.user:
        return django.http.HttpResponseForbidden

    data = json.loads(request.body)
    pk1 = data['moved_pk']
    pk2 = data['reference_pk']

    test1 = django.shortcuts.get_object_or_404(problems.models.TestCase, pk=pk1)
    test2 = django.shortcuts.get_object_or_404(problems.models.TestCase, pk=pk2)

    number1 = test1.number
    number2 = test2.number
    with django.db.transaction.atomic():
        test1.number = 0
        test1.save()
        test2.number = number1
        test2.save()
        test1.number = number2
        test1.save()

    return HttpResponse('Ok')


def problem_view(request, pk):
    return django.http.HttpResponse('бла бла бла')
