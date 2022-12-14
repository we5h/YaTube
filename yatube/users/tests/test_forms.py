from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserCreateFormTests(TestCase):
    """Проверка форм приложения Users"""

    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        """Валидная форма создает пользователя в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Тестовый Вася',
            'last_name': 'Тестовый Пупкин',
            'username': 'ТестовыйVasyan',
            'email': 'vasyannateste@mail.ru',
            'password1': 'testPASS1234',
            'password2': 'testPASS1234'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                first_name='Тестовый Вася',
                last_name='Тестовый Пупкин',
                username='ТестовыйVasyan',
                email='vasyannateste@mail.ru',
            ).exists()
        )
