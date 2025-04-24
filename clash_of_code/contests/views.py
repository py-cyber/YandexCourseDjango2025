from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
import django.db.models
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView

import contests.forms
import contests.models
import problems.forms
import problems.models
import submissions.models


class ContestCreateView(LoginRequiredMixin, CreateView):
    model = contests.models.Contest
    form_class = contests.forms.ContestForm
    template_name = 'contests/create.html'

    def form_valid(self, form):
        tz_offset = int(self.request.COOKIES.get('tz_offset', 0))

        if form.cleaned_data['start_time']:
            user_local_start = form.cleaned_data['start_time']
            form.instance.start_time = user_local_start - timezone.timedelta(
                minutes=tz_offset,
            )

        if form.cleaned_data['end_time']:
            user_local_end = form.cleaned_data['end_time']
            form.instance.end_time = user_local_end - timezone.timedelta(
                minutes=tz_offset,
            )

        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('contests:detail', kwargs={'pk': self.object.pk})


class ContestDetailView(LoginRequiredMixin, DetailView):
    model = contests.models.Contest
    template_name = 'contests/detail.html'
    queryset = contests.models.Contest.objects.select_related('created_by')
    context_object_name = 'contest'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        contest = self.object
        user = self.request.user

        if not (
            contest.is_public
            or contest.created_by == user
            or contest.participants.filter(id=user.id).exists()
            or user.is_staff
        ):
            raise PermissionDenied('Недостаточно прав')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contest = self.object
        now = timezone.now()
        user = self.request.user

        tz_offset = int(self.request.COOKIES.get('tz_offset', 0))
        contest.display_start_time = contest.start_time + timezone.timedelta(
            minutes=tz_offset,
        )
        contest.display_end_time = contest.end_time + timezone.timedelta(
            minutes=tz_offset,
        )

        solved_problems = set()
        is_registered = (
            contest.participants.filter(id=self.request.user.id).exists()
            or user.is_staff
            or contest.created_by == user
        )
        qs_sub = submissions.models.Submission
        if (now >= contest.start_time) and is_registered:
            solved_problems = set(
                qs_sub.objects.filter(
                    user=self.request.user,
                    contest=contest,
                    verdict='AC',
                ).values_list('problem_id', flat=True),
            )

        context.update(
            {
                'is_past': now > contest.end_time,
                'is_running': contest.start_time <= now <= contest.end_time,
                'is_upcoming': now < contest.start_time,
                'is_registered': is_registered,
                'is_creator': contest.created_by == self.request.user,
                'problems': contest.contestproblem_set.all()
                .select_related('problem')
                .order_by('order'),
                'duration': contest.end_time - contest.start_time,
                'solved_problems': solved_problems,
            },
        )

        if self.request.user.is_staff:
            context['participants'] = contest.participants.all().order_by('username')

        return context


class ContestRegisterView(LoginRequiredMixin, CreateView):
    model = contests.models.ContestRegistration
    fields = []
    template_name = 'contests/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = get_object_or_404(
            contests.models.Contest,
            pk=self.kwargs['pk'],
        )
        return context

    def form_valid(self, form):
        contest = get_object_or_404(contests.models.Contest, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.contest = contest
        form.instance.is_approved = contest.is_public
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('contests:detail', kwargs={'pk': self.kwargs['pk']})


class ContestStandingsView(TemplateView):
    template_name = 'contests/standings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contest = get_object_or_404(contests.models.Contest, pk=self.kwargs['pk'])

        contest_problems = contest.contestproblem_set.select_related(
            'problem',
        ).order_by('order')
        qs_sub = submissions.models.Submission
        all_submissions = (
            qs_sub.objects.filter(contest=contest)
            .select_related('user', 'problem')
            .order_by('submitted_at')
        )
        registrations = contest.contestregistration_set.filter(
            is_approved=True,
        ).select_related('user')

        standings = []
        for registration in registrations:
            user = registration.user
            user_solutions = {}
            total_points = 0
            total_penalty = 0

            for cp in contest_problems:
                problem_subs = [
                    s
                    for s in all_submissions
                    if s.user == user and s.problem == cp.problem
                ]

                ac_sub = next((s for s in problem_subs if s.verdict == 'AC'), None)
                attempts = len(
                    [
                        s
                        for s in problem_subs
                        if not ac_sub or s.submitted_at <= ac_sub.submitted_at
                    ],
                )

                if ac_sub:
                    penalty_time = max(
                        0,
                        (ac_sub.submitted_at - contest.start_time).total_seconds()
                        // 60,
                    )
                    penalty = penalty_time + (20 * (attempts - 1))
                    points = max(0, cp.points - penalty)

                    user_solutions[str(cp.problem.id)] = {
                        'verdict': 'AC',
                        'points': points,
                        'penalty': penalty,
                        'time': ac_sub.submitted_at.strftime('%H:%M'),
                        'attempts': attempts,
                        'problem_id': cp.problem.id,
                    }
                    total_points += points
                    total_penalty += penalty
                elif attempts > 0:
                    user_solutions[str(cp.problem.id)] = {
                        'verdict': 'WA',
                        'points': 0,
                        'attempts': attempts,
                        'problem_id': cp.problem.id,
                    }

            standings.append(
                {
                    'user': user,
                    'total_points': total_points,
                    'total_penalty': total_penalty,
                    'solutions': user_solutions,
                    'solutions_list': list(user_solutions.values()),
                },
            )

        standings.sort(key=lambda x: (-x['total_points'], x['total_penalty']))

        context.update(
            {
                'contest': contest,
                'standings': standings,
                'problems': contest_problems,
            },
        )
        return context


class AddProblemToContestView(LoginRequiredMixin, CreateView):
    form_class = contests.forms.AddProblemToContestForm
    template_name = 'contests/add_problem.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.contest = get_object_or_404(
            contests.models.Contest.objects.select_related('created_by'),
            pk=self.kwargs['contest_id'],
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(
                request,
                'Пожалуйста, войдите в систему для доступа к этой странице',
            )
            return redirect('login')

        if not (
            request.user.is_staff
            or request.user == self.contest.created_by
            or request.user.is_superuser
        ):
            raise PermissionDenied('Недостаточно прав')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.contest
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['contest'] = self.contest

        query = problems.models.Problem
        conditions = django.db.models.Q(author=self.request.user) | django.db.models.Q(
            is_public=True,
        )
        kwargs['problem_queryset'] = (
            query.objects.filter(
                conditions,
            )
            .select_related('author')
            .only('id', 'title', 'author__username', 'is_public')
        )
        return kwargs

    def form_valid(self, form):
        try:
            form.instance.contest = self.contest

            if not form.instance.order:
                query = contests.models.ContestProblem
                last_order = (
                    query.objects.filter(
                        contest=self.contest,
                    ).aggregate(
                        django.db.models.Max('order'),
                    )['order__max']
                    or 0
                )
                form.instance.order = last_order + 1

            if form.cleaned_data['new_problem']:
                problem_form = problems.forms.ProblemsForm(self.request.POST)
                if problem_form.is_valid():
                    problem = problem_form.save(commit=False)
                    problem.author = self.request.user
                    problem.save()
                    form.instance.problem = problem
                else:
                    for field, errors in problem_form.errors.items():
                        for error in errors:
                            form.add_error(None, f'{field}: {error}')

                    return self.form_invalid(form)
            else:
                form.instance.problem = form.cleaned_data['problem']

            form.instance.contest = self.contest
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f'Ошибка при отправке письма: {str(e)}')
            return self.form_invalid(form)

    def get_success_url(self):
        return redirect('contests:detail', pk=self.kwargs['contest_id']).url


class ContestListView(ListView):
    model = contests.models.Contest
    template_name = 'contests/list.html'
    context_object_name = 'contests'
    ordering = ['start_time']

    def get_queryset(self):
        tz_offset = int(self.request.COOKIES.get('tz_offset', 0))

        queryset = self.model.objects.select_related(
            'created_by',
            'created_by__profile',
        ).filter(is_public=True)

        return queryset.annotate(
            display_start_time=django.db.models.F('start_time')
            + timezone.timedelta(minutes=tz_offset),
            display_end_time=django.db.models.F('end_time')
            + timezone.timedelta(minutes=tz_offset),
            contests=django.db.models.Case(
                django.db.models.When(
                    start_time__gt=timezone.now(),
                    then=django.db.models.Value('upcoming'),
                ),
                django.db.models.When(
                    end_time__lt=timezone.now(),
                    then=django.db.models.Value('finished'),
                ),
                default=django.db.models.Value('running'),
                output_field=django.db.models.CharField(),
            ),
        ).order_by('start_time')

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class ContestSubmissionsView(LoginRequiredMixin, ListView):
    model = submissions.models.Submission
    template_name = 'contests/contest_submissions.html'
    context_object_name = 'my_submissions'

    def get_queryset(self):
        self.contest = get_object_or_404(contests.models.Contest, pk=self.kwargs['pk'])

        return (
            self.model.objects.filter(
                user=self.request.user,
                contest=self.contest,
                problem__in=self.contest.contestproblem_set.values('problem'),
            )
            .select_related('problem', 'user')
            .order_by('-submitted_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contest'] = self.contest

        if self.request.user.is_staff or self.request.user == self.contest.created_by:
            contest_problem_ids = contests.models.ContestProblem.objects.filter(
                contest=self.contest,
            ).values_list('problem_id', flat=True)

            context['all_submissions'] = self.model.objects.filter(
                contest=self.contest,
                problem_id__in=contest_problem_ids,
                submitted_at__range=(
                    self.contest.start_time,
                    self.contest.end_time,
                ),
            )
            context['all_submissions'].select_related('problem', 'user')
            context['all_submissions'].order_by('-submitted_at')

        tz_offset = int(self.request.COOKIES.get('tz_offset', 0))
        for submission in context['my_submissions']:
            submission.display_submitted_at = (
                submission.submitted_at + timezone.timedelta(minutes=tz_offset)
            )

        return context
