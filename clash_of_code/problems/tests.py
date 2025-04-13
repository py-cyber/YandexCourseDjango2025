import http

import django.shortcuts
import django.test

import problems.models
import users.models


class ProblemTests(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()
        self.user = users.models.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
        )
        self.client.force_login(self.user)

    def test_url_problems_create(self):
        response = django.test.Client().get(
            django.shortcuts.reverse('problems:create_task'),
        )

        self.assertEqual(response.status_code, http.HTTPStatus.FOUND)

    def test_create_problem(self):
        problems_count = problems.models.Problem.objects.count()

        data = {
            'title': 'тест',
            'description': 'тест',
            'difficult': 1,
            'is_public': True,
            'author_solution': 'print("test")',
            'author_language': 'Py3.11',
            'input_format': 'afa',
            'output_format': 'faf',
            'time_limit': 1,
            'memory_limit': 64,
        }
        self.client.post(django.shortcuts.reverse('problems:create_task'), data=data)

        self.assertEqual(problems_count + 1, problems.models.Problem.objects.count())

    def test_create_unavailable_problem(self):
        problems_count = problems.models.Problem.objects.count()

        data = {
            'title': 'тест',
            'description': 'тест',
            'difficult': 1,
            'is_public': True,
            'author_solution': '',
            'author_language': 'Py3.11',
            'input_format': 'afa',
            'output_format': 'faf',
            'time_limit': 1,
            'memory_limit': 32,
        }

        self.client.post(django.shortcuts.reverse('problems:create_task'), data=data)
        self.assertEqual(problems_count, problems.models.Problem.objects.count())
