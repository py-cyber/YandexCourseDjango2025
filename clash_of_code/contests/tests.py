from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

import contests.forms
import contests.models
import problems.models

User = get_user_model()


class ContestViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass',
        )
        cls.creator_user = User.objects.create_user(
            username='creator',
            email='creator@example.com',
            password='creatorpass',
        )
        cls.participant_user = User.objects.create_user(
            username='participant',
            email='participant@example.com',
            password='participantpass',
        )
        cls.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass',
        )

        cls.public_problem = problems.models.Problem.objects.create(
            title='Public Problem',
            description='Public problem description',
            author=cls.creator_user,
            is_public=True,
            difficult=52,
        )
        cls.private_problem = problems.models.Problem.objects.create(
            title='Private Problem',
            description='Private problem description',
            author=cls.creator_user,
            is_public=False,
            difficult=52,
        )

        cls.now = timezone.now()
        cls.one_hour = timezone.timedelta(hours=1)
        cls.one_day = timezone.timedelta(days=1)

    def setUp(self):
        self.past_contest = contests.models.Contest.objects.create(
            name='Past Contest',
            description='Past contest description',
            created_by=self.creator_user,
            start_time=self.now - self.one_day - self.one_hour,
            end_time=self.now - self.one_day,
            is_public=True,
        )
        self.running_contest = contests.models.Contest.objects.create(
            name='Running Contest',
            description='Running contest description',
            created_by=self.creator_user,
            start_time=self.now - self.one_hour,
            end_time=self.now + self.one_hour,
            is_public=True,
        )
        self.future_contest = contests.models.Contest.objects.create(
            name='Future Contest',
            description='Future contest description',
            created_by=self.creator_user,
            start_time=self.now + self.one_day,
            end_time=self.now + self.one_day + self.one_hour,
            is_public=True,
        )
        self.private_contest = contests.models.Contest.objects.create(
            name='Private Contest',
            description='Private contest description',
            created_by=self.creator_user,
            start_time=self.now - self.one_hour,
            end_time=self.now + self.one_hour,
            is_public=False,
        )
        self.past_problem = contests.models.ContestProblem.objects.create(
            contest=self.past_contest,
            problem=self.public_problem,
            points=100,
            order=1,
        )
        self.running_problem = contests.models.ContestProblem.objects.create(
            contest=self.running_contest,
            problem=self.public_problem,
            points=100,
            order=1,
        )

        contests.models.ContestRegistration.objects.create(
            contest=self.running_contest,
            user=self.participant_user,
            is_approved=True,
        )

    def test_contest_status_properties(self):
        self.assertEqual(self.past_contest.status, 'finished')
        self.assertEqual(self.running_contest.status, 'running')
        self.assertEqual(self.future_contest.status, 'upcoming')

    def test_contest_list_view_ordering(self):
        response = self.client.get(reverse('contests:list'))
        contests = response.context['contests']

        self.assertEqual(contests[0].name, 'Running Contest')
        self.assertEqual(contests[1].name, 'Future Contest')
        self.assertEqual(contests[2].name, 'Past Contest')

    def test_contest_detail_view_access(self):
        url = reverse('contests:detail', kwargs={'pk': self.running_contest.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username='regular', password='regularpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='participant', password='participantpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='creator', password='creatorpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='admin', password='adminpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('contests:detail', kwargs={'pk': self.private_contest.pk})

        self.client.login(username='regular', password='regularpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='creator', password='creatorpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='admin', password='adminpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contest_detail_view_context(self):
        self.client.login(username='participant', password='participantpass')
        url = reverse('contests:detail', kwargs={'pk': self.running_contest.pk})
        response = self.client.get(url)

        context = response.context
        self.assertEqual(context['contest'], self.running_contest)
        self.assertTrue(context['is_running'])
        self.assertFalse(context['is_past'])
        self.assertFalse(context['is_upcoming'])
        self.assertTrue(context['is_registered'])
        self.assertEqual(list(context['problems']), [self.running_problem])
        # self.assertIn(self.public_problem.id, context['solved_problems']) # noqa

    def test_contest_create_view(self):
        self.client.login(username='creator', password='creatorpass')
        url = reverse('contests:create')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        start_time = self.now.replace(second=0, microsecond=0) + timezone.timedelta(
            days=2,
        )
        end_time = start_time + timezone.timedelta(hours=3)

        with mock.patch('django.utils.timezone.now', return_value=self.now):
            response = self.client.post(
                url,
                {
                    'name': 'New Contest',
                    'description': 'New contest description',
                    'start_time': start_time.strftime('%Y-%m-%d %H:%M'),
                    'end_time': end_time.strftime('%Y-%m-%d %H:%M'),
                    'is_public': 'on',
                    'registration_open': 'on',
                },
            )

            self.assertEqual(response.status_code, 302)

            new_contest = contests.models.Contest.objects.get(name='New Contest')
            self.assertEqual(new_contest.created_by, self.creator_user)
            self.assertEqual(new_contest.start_time, start_time)
            self.assertEqual(new_contest.end_time, end_time)
            self.assertTrue(new_contest.is_public)

    def test_contest_create_with_timezone_offset(self):
        self.client.login(username='creator', password='creatorpass')
        url = reverse('contests:create')

        self.client.cookies['tz_offset'] = '180'

        user_local_start = self.now.replace(
            second=0,
            microsecond=0,
        ) + timezone.timedelta(days=1)
        user_local_end = user_local_start + timezone.timedelta(hours=2)

        response = self.client.post(
            url,
            {
                'name': 'TZ Contest',
                'description': 'Timezone test contest',
                'start_time': user_local_start.strftime('%Y-%m-%d %H:%M'),
                'end_time': user_local_end.strftime('%Y-%m-%d %H:%M'),
                'is_public': 'on',
                'registration_open': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)

        contest = contests.models.Contest.objects.get(name='TZ Contest')

        self.assertEqual(
            contest.start_time,
            user_local_start - timezone.timedelta(minutes=180),
        )
        self.assertEqual(
            contest.end_time,
            user_local_end - timezone.timedelta(minutes=180),
        )

    def test_contest_register_view(self):
        self.client.login(username='regular', password='regularpass')
        url = reverse('contests:register', kwargs={'pk': self.running_contest.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)

        registration = contests.models.ContestRegistration.objects.get(
            contest=self.running_contest,
            user=self.regular_user,
        )

        self.assertTrue(registration.is_approved)

        url = reverse('contests:register', kwargs={'pk': self.private_contest.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)

        registration = contests.models.ContestRegistration.objects.get(
            contest=self.private_contest,
            user=self.regular_user,
        )

        self.assertFalse(registration.is_approved)

    def test_add_problem_to_contest_view(self):
        self.client.login(username='creator', password='creatorpass')
        url = reverse(
            'contests:add_problem',
            kwargs={'contest_id': self.running_contest.pk},
        )

        new_problem = problems.models.Problem.objects.create(
            title='New Test Problem',
            description='Test problem description',
            author=self.creator_user,
            is_public=True,
            difficult=55,
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            url,
            {
                'problem': new_problem.pk,
                'new_problem': False,
                'points': 50,
                'order': 2,
            },
        )

        self.assertEqual(response.status_code, 302)

        contest_problem = contests.models.ContestProblem.objects.get(
            contest=self.running_contest,
            problem=new_problem,
        )
        self.assertEqual(contest_problem.points, 50)
        self.assertEqual(contest_problem.order, 2)

    def test_add_problem_to_contest_permissions(self):
        url = reverse(
            'contests:add_problem',
            kwargs={'contest_id': self.running_contest.pk},
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.login(username='regular', password='regularpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='participant', password='participantpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        self.client.login(username='creator', password='creatorpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username='admin', password='adminpass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contest_form_validation(self):
        form_data = {
            'name': 'Test Contest',
            'description': 'Test description',
            'start_time': self.now + timezone.timedelta(hours=1),
            'end_time': self.now,
            'is_public': True,
            'registration_open': True,
        }

        form = contests.forms.ContestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Время окончания должно быть позже времени начала',
            str(form.errors),
        )

        form_data['start_time'] = self.now - timezone.timedelta(days=1)
        form_data['end_time'] = self.now + timezone.timedelta(hours=1)
        form = contests.forms.ContestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Время начала не может быть в прошлом', str(form.errors))

        form_data['start_time'] = self.now + timezone.timedelta(days=1)
        form_data['end_time'] = self.now + timezone.timedelta(days=1, hours=2)
        form = contests.forms.ContestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_problem_form_validation(self):
        form_data = {'problem': None, 'new_problem': False, 'points': 100, 'order': 1}

        form = contests.forms.AddProblemToContestForm(
            data=form_data,
            contest=self.running_contest,
            user=self.creator_user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Выберите существующую задачу или создайте новую',
            str(form.errors),
        )

        form_data['problem'] = self.private_problem.pk
        form = contests.forms.AddProblemToContestForm(
            data=form_data,
            contest=self.running_contest,
            user=self.regular_user,
        )
        self.assertFalse(form.is_valid())

        contests.models.ContestProblem.objects.filter(
            contest=self.running_contest,
            problem=self.public_problem,
        ).delete()

        form_data['problem'] = self.public_problem.pk
        form = contests.forms.AddProblemToContestForm(
            data=form_data,
            contest=self.running_contest,
            user=self.regular_user,
        )
        self.assertTrue(form.is_valid())

        form_data = {
            'new_problem': True,
            'title': 'New Problem Title',
            'description': 'New problem description',
            'points': 100,
            'order': 1,
        }
        form = contests.forms.AddProblemToContestForm(
            data=form_data,
            contest=self.running_contest,
            user=self.regular_user,
        )
        self.assertTrue(form.is_valid())
