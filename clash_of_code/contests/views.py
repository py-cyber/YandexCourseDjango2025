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

        tz_offset = int(self.request.COOKIES.get('tz_offset', 0))

        contest.display_start_time = contest.start_time + timezone.timedelta(
            minutes=tz_offset,
        )
        contest.display_end_time = contest.end_time + timezone.timedelta(
            minutes=tz_offset,
        )

        context.update(
            {
                'is_past': now > contest.end_time,
                'is_running': contest.start_time <= now <= contest.end_time,
                'is_upcoming': now < contest.start_time,
                'is_registered': contest.participants.filter(
                    id=self.request.user.id,
                ).exists(),
                'is_creator': contest.created_by == self.request.user,
                'problems': contest.contestproblem_set.all()
                .select_related('problem')
                .order_by('order'),
                'duration': contest.end_time - contest.start_time,
            },
        )

        if context['is_running'] or context['is_past']:
            if context['is_registered']:
                query = contests.models.ContestSolution.objects
                context['solved_problems'] = set(
                    query.filter(
                        user=self.request.user,
                        contest_problem__contest=contest,
                    ).values_list(
                        'contest_problem__problem_id',
                        flat=True,
                    ),
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

        standings = []
        for registration in contest.contestregistration_set.filter(is_approved=True):
            user = registration.user
            solutions = contests.models.ContestSolution.objects.filter(
                user=user,
                contest_problem__contest=contest,
            )

            total_points = sum(s.contest_problem.points for s in solutions)
            total_penalty = sum(s.penalty for s in solutions)

            standings.append(
                {
                    'user': user,
                    'total_points': total_points,
                    'total_penalty': total_penalty,
                    'solutions': solutions,
                },
            )

        context.update(
            {
                'contest': contest,
                'standings': sorted(
                    standings,
                    key=lambda x: (-x['total_points'], x['total_penalty']),
                ),
                'problems': contest.contestproblem_set.all().order_by('order'),
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
