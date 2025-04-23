import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
import django.db.transaction
import django.http
from django.http import HttpResponse
import django.shortcuts
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

import contests.models
import problems.forms
import problems.models
import problems.tasks
import submissions.models
from submissions.tasks import check_solution


logger = logging.getLogger(__name__)


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


class ProblemsUpdateView(LoginRequiredMixin, UpdateView, UserPassesTestMixin):
    model = problems.models.Problem
    queryset = problems.models.Problem.objects.select_related('author')
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

    def post(self, request, pk):
        problem = django.shortcuts.get_object_or_404(problems.models.Problem, pk=pk)
        if problem.author != request.user:
            return django.http.HttpResponseForbidden

        form = problems.forms.TestForm(request.POST)
        if not form.is_valid():
            return django.shortcuts.redirect(
                django.shortcuts.reverse('problems:tests', args=[pk]),
            )

        input_data = form.cleaned_data['input_data']
        output_data = form.cleaned_data['output_data']
        number = form.cleaned_data['number']
        is_sample = form.cleaned_data['is_sample']
        pk_test = form.cleaned_data['pk']
        if pk_test is None:
            problems.models.TestCase.objects.create(
                input_data=input_data,
                output_data=output_data,
                is_sample=is_sample,
                problem=problem,
                number=number,
            )
        else:
            test = django.shortcuts.get_object_or_404(
                problems.models.TestCase,
                pk=pk_test,
            )
            test.input_data = input_data
            test.output_data = output_data
            test.is_sample = is_sample

            test.full_clean()
            test.save()

        problem.is_correct = False
        problem.save()

        return django.shortcuts.redirect(
            django.shortcuts.reverse('problems:tests', args=[pk]),
        )


class UpdateTestOrderView(django.views.View):
    def post(self, request, pk):
        problem = django.shortcuts.get_object_or_404(problems.models.Problem, pk=pk)
        if problem.author != request.user:
            return django.http.HttpResponseForbidden

        data = json.loads(request.body)
        pk1 = int(data['moved_pk'])
        pk2 = int(data['reference_pk'])

        test1 = django.shortcuts.get_object_or_404(problems.models.TestCase, pk=pk1)
        test2 = django.shortcuts.get_object_or_404(problems.models.TestCase, pk=pk2)

        number1 = test1.number
        number2 = test2.number
        with django.db.transaction.atomic():
            test1.number = 999999999
            test1.save()
            test2.number = number1
            test2.save()
            test1.number = number2
            test1.save()

        return HttpResponse('Ok')


class DeleteTestView(LoginRequiredMixin, DeleteView, UserPassesTestMixin):
    model = problems.models.TestCase
    template_name = 'problems/check_delete_test.html'

    def get_success_url(self):
        return reverse('problems:tests', kwargs={'pk': self.object.problem.pk})

    def test_func(self):
        test = self.get_object()
        return self.request.user == test.problem.author


class AllMyTaskView(LoginRequiredMixin, ListView):
    model = problems.models.Problem
    template_name = 'problems/my_tasks.html'
    context_object_name = 'tasks'
    paginate_by = 20

    def get_queryset(self):
        return problems.models.Problem.objects.filter(author=self.request.user)


class ProblemDetailView(View):
    template_name = 'problems/problem_detail.html'

    def get(self, request, pk):

        pf = problems.models.Problem.objects.select_related('author').prefetch_related(
            'tags',
            'tests',
        )
        problem = django.shortcuts.get_object_or_404(
            pf,
            pk=pk,
        )

        if not problem.is_public and problem.author != request.user:
            raise PermissionDenied

        sample_tests = problem.tests.filter(is_sample=True).order_by('number')

        context = {
            'problem': problem,
            'tests': sample_tests,
            'can_edit': problem.author == request.user,
            'input_format': problem.input_format,
            'output_format': problem.output_format,
            'time_limit': problem.time_limit,
            'memory_limit': problem.memory_limit,
            'tags': problem.tags.all(),
            'created_at': problem.created_at,
            'difficulty': problem.difficult,
            'languages': problems.models.LanguageChoices.choices,
        }
        return django.shortcuts.render(request, self.template_name, context)


class CheckAuthorSolutionView(View):
    def get(self, request, pk):
        task = django.shortcuts.get_object_or_404(problems.models.Problem, pk=pk)
        if task.author != request.user:
            return PermissionDenied

        task.is_correct = False
        task.status = problems.models.VerdictChoice.In_queue
        task.test_error = None
        task.logs = None
        task.save()

        problems.tasks.check_auther_solution.delay_on_commit(pk)

        return django.shortcuts.redirect(
            django.shortcuts.reverse('problems:update', args=[pk]),
        )


class SubmitSolutionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        logger.debug(f'Начало обработки submission для задачи {pk}')

        problem = get_object_or_404(problems.models.Problem, pk=pk)
        contest_id = request.POST.get('contest_id')
        code = request.POST.get('code', '').strip()
        language = request.POST.get('language', '').strip()

        logger.debug(
            f'Получены данные: contest_id={contest_id}, '
            f'language={language}, code_length={len(code)}',
        )

        if not code or not language:
            msg = 'Необходимо указать код и язык программирования'
            logger.warning(msg)
            messages.error(request, msg)
            return redirect('problems:problem', pk=pk)

        is_contest_submission = False
        contest = None

        if contest_id:
            try:
                logger.debug(f'Попытка найти контест {contest_id}')
                contest = contests.models.Contest.objects.get(id=contest_id)
                logger.debug(f'Найден контест: {contest.name}')

                current_time = timezone.now()
                logger.debug(f'Текущее время: {current_time}')
                logger.debug(
                    f'Время контеста: {contest.start_time} - {contest.end_time}',
                )

                time_ok = contest.start_time <= current_time <= contest.end_time
                problem_in_contest = contests.models.ContestProblem.objects.filter(
                    contest=contest,
                    problem=problem,
                ).exists()

                user_has_privileges = any(
                    [
                        request.user.is_staff,
                        request.user.is_superuser,
                        contest.created_by == request.user,
                    ],
                )
                user_registered = (
                    user_has_privileges
                    or contest.participants.filter(id=request.user.id).exists()
                )

                logger.debug(
                    f'Проверки: time_ok={time_ok},'
                    f' problem_in_contest={problem_in_contest},'
                    f' user_registered={user_registered}',
                )

                valid_contest = all([time_ok, problem_in_contest, user_registered])
                logger.debug(f'Контест валиден: {valid_contest}')

                if valid_contest:
                    is_contest_submission = True
                    logger.info(f'Решение будет засчитано для контеста {contest_id}')
                else:
                    msg = 'Решение не засчитано для контеста'
                    logger.warning(msg)
                    messages.warning(request, msg)

            except contests.models.Contest.DoesNotExist as e:
                msg = 'Указанный контест не существует'
                logger.error(f'{msg}: {str(e)}')
                messages.error(request, msg)

        submission_data = {
            'user': request.user,
            'problem': problem,
            'code': code,
            'language': language,
            'contest': contest if is_contest_submission else None,
        }

        logger.debug(f'Данные для submission: {submission_data}')

        try:
            submission = submissions.models.Submission.objects.create(**submission_data)
            logger.info(
                f'Создано решение: ID={submission.id}, Contest={submission.contest_id}',
            )
        except Exception as e:
            logger.error(f'Ошибка создания submission: {str(e)}')
            messages.error(request, 'Ошибка при сохранении решения')
            return redirect('problems:problem', pk=pk)

        try:
            check_solution.delay(submission.pk)
            logger.debug(
                f'Задача проверки отправлена в Celery для submission {submission.id}',
            )
        except Exception as e:
            logger.error(f'Ошибка отправки в Celery: {str(e)}')

        if is_contest_submission:
            return redirect('contests:contest_submissions', pk=contest_id)

        return redirect('problems:submission_detail', pk=submission.pk)


class MySubmissionsView(LoginRequiredMixin, ListView):
    model = submissions.models.Submission
    template_name = 'problems/my_submissions.html'
    context_object_name = 'submissions'

    def get_queryset(self):
        return self.model.objects.filter(
            user=self.request.user,
            problem_id=self.kwargs['pk'],
            contest__isnull=True,
        ).order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = get_object_or_404(
            problems.models.Problem,
            pk=self.kwargs['pk'],
        )
        tz_offset = int(self.request.COOKIES.get('tz_offset', 0))
        for submission in context['submissions']:
            submission.display_submitted_at = (
                submission.submitted_at + timezone.timedelta(minutes=tz_offset)
            )

        return context


class SubmissionDetailView(LoginRequiredMixin, DetailView):
    model = submissions.models.Submission
    template_name = 'problems/submission_detail.html'
    context_object_name = 'submission'

    def get_queryset(self):
        return submissions.models.Submission.objects.select_related(
            'user',
            'problem',
            'contest',
        ).prefetch_related('problem__tests')

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.has_permission():
            raise PermissionDenied('У вас нет прав для просмотра этого решения')

        return super().dispatch(request, *args, **kwargs)

    def has_permission(self):
        submission = self.object
        user = self.request.user

        if user == submission.user:
            return True

        if submission.contest:
            return (
                submission.contest.participants.filter(id=user.id).exists()
                or submission.contest.created_by == user
                or user.is_staff
            )

        return user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object

        if submission.contest:
            context['contest'] = submission.contest
            context['contest_problem'] = contests.models.ContestProblem.objects.filter(
                contest=submission.contest,
                problem=submission.problem,
            ).first()

        if hasattr(submission, 'test_results'):
            context['test_results'] = submission.test_results.all()

        return context
