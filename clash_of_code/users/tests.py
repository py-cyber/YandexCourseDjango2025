from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class LoginTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
        )

    def test_login_with_email(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'test@example.com',
                'password': 'testpassword123',
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_login_with_username(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'testuser',
                'password': 'testpassword123',
            },
        )
        self.assertEqual(response.status_code, 302)

    def test_invalid_login(self):
        response = self.client.post(
            reverse('login'),
            {
                'username': 'wrong@example.com',
                'password': 'wrongpassword',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Пожалуйста, введите правильные имя пользователя и пароль.'
            ' Оба поля могут быть чувствительны к регистру.',
        )


class SignUpTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')

    def test_signup_with_valid_data(self):
        response = self.client.post(
            self.signup_url,
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'complexpassword123',
                'password2': 'complexpassword123',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_signup_with_existing_username(self):
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpassword123',
        )

        response = self.client.post(
            self.signup_url,
            {
                'username': 'existinguser',
                'email': 'newuser@example.com',
                'password1': 'complexpassword123',
                'password2': 'complexpassword123',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Пользователь с таким именем уже существует.',
        )

    def test_signup_with_non_matching_passwords(self):
        response = self.client.post(
            self.signup_url,
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'complexpassword123',
                'password2': 'differentpassword',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Введенные пароли не совпадают.')


__all__ = []
