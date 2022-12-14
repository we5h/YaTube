from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    """Класс проверки URL's"""

    @classmethod
    def setUpClass(cls):
        """Создаем тестируемые объекты"""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        """Имитация создания запроса от клиента"""
        self.guest_client = Client()  # Гость неавторизованный
        self.unknown_user = Client()
        # Авторизированный пользователь
        self.unknown_user.force_login(StaticURLTests.user2)
        self.post_owner = Client()
        self.post_owner.force_login(StaticURLTests.user)  # Автор поста

    def test_task_url_exists_at_desired_location(self):
        """Проверка доступа URL's для всех"""
        slug = StaticURLTests.group.slug
        username = StaticURLTests.user.username
        post_id = StaticURLTests.post.id
        address_dict = {
            '/': HTTPStatus.OK,
            f'/group/{slug}/': HTTPStatus.OK,
            f'/profile/{username}/': HTTPStatus.OK,
            f'/posts/{post_id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        for address, code in address_dict.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_task_url_post_owner(self):
        """Проверка URL's для автора поста"""
        post_id = StaticURLTests.post.id
        response = self.post_owner.get(f'/posts/{post_id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_url_redirect(self):
        """Проверка URL's для неавторизованного пользователя"""
        post_id = StaticURLTests.post.id
        response = self.guest_client.get(
            f'/posts/{post_id}/edit/', follow=True
        )
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{post_id}/edit/')
        )

    def test_task_url_redirect_authorized(self):
        """Проверка URL's для авторизованного пользователя"""
        post_id = StaticURLTests.post.id
        response = self.unknown_user.get(
            f'/posts/{post_id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/posts/{post_id}/'
        )

    def test_task_create_authorized(self):
        """Проверка URLa создания поста для авторизованного юзера"""
        response = self.unknown_user.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_task_correct_template(self):
        """Тест соответсвия адреса шаблону"""
        slug = StaticURLTests.group.slug
        post_id = StaticURLTests.post.id
        username = StaticURLTests.user.username
        address_temp = {
            '/': 'posts/index.html',
            f'/group/{slug}/': 'posts/group_list.html',
            f'/profile/{username}/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
            f'/posts/{post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in address_temp.items():
            with self.subTest(adress=address):
                response = self.post_owner.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_comment_guest_redirect(self):
        """Гость попадает на страницу логина при комменте"""
        post_id = StaticURLTests.post.id
        response = self.guest_client.get(
            f'/posts/{post_id}/comment/', follow=True
        )
        self.assertRedirects(
            response, (f'/auth/login/?next=/posts/{post_id}/comment/')
        )

    def test_post_comment_user(self):
        """Пользователь постит коммент"""
        post_id = StaticURLTests.post.id
        response = self.unknown_user.get(
            f'/posts/{post_id}/comment/', follow=True
        )
        self.assertRedirects(
            response, (f'/posts/{post_id}/')
        )
