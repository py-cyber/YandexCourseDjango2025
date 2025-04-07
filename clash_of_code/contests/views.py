from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, TemplateView

from contests.forms import ContestForm
import contests.models


class ContestCreateView(LoginRequiredMixin, CreateView):
    model = contests.models.Contest
    form_class = ContestForm
    template_name = 'contests/create.html'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('contests:detail', kwargs={'pk': self.object.pk})


class ContestDetailView(LoginRequiredMixin, DetailView):
    model = contests.models.Contest
    template_name = 'contests/detail.html'
    context_object_name = 'contest'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contest = self.object
        now = timezone.now()

        context.update(
            {
                'is_past': now > contest.end_time,
                'is_running': contest.start_time <= now <= contest.end_time,
                'is_upcoming': now < contest.start_time,
                'is_registered': contest.participants.filter(
                    id=self.request.user.id,
                ).exists(),
                'is_creator': contest.created_by == self.request.user,
                'problems': contest.contestproblem_set.all().order_by('order'),
            },
        )

        if context['is_running'] or context['is_past']:
            if context['is_registered']:
                context['solved_problems'] = set(
                    contests.models.ContestSolution.objects.filter(
                        user=self.request.user,
                        contest_problem__contest=contest,
                    ).values_list(
                        'contest_problem__problem_id',
                        flat=True,
                    )
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
            contests.models.Contest, pk=self.kwargs['pk']
        )
        return context

    def form_valid(self, form):
        contest = get_object_or_404(contests.models.Contest, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        form.instance.contest = contest
        form.instance.is_approved = contest.is_public
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('contest:detail', kwargs={'pk': self.kwargs['pk']})


class ContestStandingsView(TemplateView):
    template_name = 'contests/standings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contest = get_object_or_404(contests.models.Contest, pk=self.kwargs['pk'])

        standings = []
        for registration in contest.contestregistration_set.filter(is_approved=True):
            user = registration.user
            solutions = contests.models.ContestSolution.objects.filter(
                user=user, contest_problem__contest=contest
            )

            total_points = sum(s.contest_problem.points for s in solutions)
            total_penalty = sum(s.penalty for s in solutions)

            standings.append(
                {
                    'user': user,
                    'total_points': total_points,
                    'total_penalty': total_penalty,
                    'solutions': solutions,
                }
            )

        context.update(
            {
                'contest': contest,
                'standings': sorted(
                    standings, key=lambda x: (-x['total_points'], x['total_penalty'])
                ),
                'problems': contest.contestproblem_set.all().order_by('order'),
            }
        )
        return context
