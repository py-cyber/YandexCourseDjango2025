import http

import django.shortcuts
import django.test

import problems.models
import problems.tasks
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


class TestSystemTests(django.test.TestCase):
    def setUp(self):
        self.user = users.models.User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
        )

    def test_correct_task(self):
        correct_task = problems.models.Problem(
            title='test',
            description='test',
            difficult=10,
            author_solution='print(input())',
            author_language=problems.models.LanguageChoices.Python_3_11,
            author=self.user,
            input_format='test',
            output_format='test',
        )
        correct_task.save()

        test1 = problems.models.TestCase(
            problem=correct_task,
            input_data='1',
            output_data='1',
            number=0,
        )
        test1.save()

        problems.tasks.check_auther_solution(correct_task.pk)
        correct_task = problems.models.Problem.objects.get(pk=correct_task.pk)
        self.assertEqual(correct_task.is_correct, True)
        self.assertEqual(correct_task.status, problems.models.VerdictChoice.Accept)
        self.assertIsNone(correct_task.logs, correct_task.logs)
        self.assertIsNone(correct_task.test_error, correct_task.test_error)

    def test_incorrect_task(self):
        correct_task = problems.models.Problem(
            title='test',
            description='test',
            difficult=10,
            author_solution='print(input())',
            author_language=problems.models.LanguageChoices.Python_3_11,
            author=self.user,
            input_format='test',
            output_format='test',
        )
        correct_task.save()

        incorrect_test1 = problems.models.TestCase(
            problem=correct_task,
            input_data='1',
            output_data='2',
            number=1,
        )
        incorrect_test1.save()

        problems.tasks.check_auther_solution(correct_task.pk)
        correct_task = problems.models.Problem.objects.get(pk=correct_task.pk)
        self.assertEqual(correct_task.is_correct, False)
        self.assertEqual(
            correct_task.status,
            problems.models.VerdictChoice.Wrong_answer,
        )
        self.assertIsNotNone(correct_task.logs, correct_task.logs)
        self.assertIsNotNone(correct_task.test_error, correct_task.test_error)

    def test_long_task(self):
        incorrect_task = problems.models.Problem(
            title='test',
            description='test',
            difficult=10,
            author_solution='input()\nfor _ in range(10000000000): pass',
            author_language=problems.models.LanguageChoices.Python_3_11,
            author=self.user,
            input_format='test',
            output_format='test',
        )
        incorrect_task.save()

        incorrect_test1 = problems.models.TestCase(
            problem=incorrect_task,
            input_data='1',
            output_data='2',
            number=1,
        )
        incorrect_test1.save()

        problems.tasks.check_auther_solution(incorrect_task.pk)
        incorrect_task = problems.models.Problem.objects.get(pk=incorrect_task.pk)
        self.assertEqual(incorrect_task.is_correct, False)
        self.assertEqual(
            incorrect_task.status,
            problems.models.VerdictChoice.Time_limit,
            incorrect_task.logs,
        )
        self.assertIsNotNone(incorrect_task.logs, incorrect_task.logs)
        self.assertIsNotNone(incorrect_task.test_error, incorrect_task.test_error)

    def test_runtime_error_task(self):
        incorrect_task = problems.models.Problem(
            title='test',
            description='test',
            difficult=10,
            author_solution='for _ in range(10',
            author_language=problems.models.LanguageChoices.Python_3_11,
            author=self.user,
            input_format='test',
            output_format='test',
        )
        incorrect_task.save()

        incorrect_test1 = problems.models.TestCase(
            problem=incorrect_task,
            input_data='1',
            output_data='2',
            number=1,
        )
        incorrect_test1.save()

        problems.tasks.check_auther_solution(incorrect_task.pk)
        incorrect_task = problems.models.Problem.objects.get(pk=incorrect_task.pk)
        self.assertEqual(incorrect_task.is_correct, False)
        self.assertEqual(
            incorrect_task.status,
            problems.models.VerdictChoice.Runtime_error,
            incorrect_task.logs,
        )
        self.assertIsNotNone(incorrect_task.logs, incorrect_task.logs)
        self.assertIsNotNone(incorrect_task.test_error, incorrect_task.test_error)
