import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
FOLLOW_FLAG = 1
UNFOLLOW_FLAG = 0


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='post_author')
        cls.user3 = User.objects.create_user(username='post_author2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post3 = Post.objects.create(
            text='Тестовый текст3',
            author=cls.user3,
            group=cls.group,
            image=uploaded
        )
        cls.post2 = Post.objects.create(
            text='Тестовый текст2',
            author=cls.user2,
            group=cls.group,
            image=uploaded
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='Тестовый коммент',
            author=cls.user,
            post=cls.post
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TaskPagesTests.user)
        self.guest_client = Client()

    def test_created_post_exists_in_index(self):
        """Пост создается на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post, TaskPagesTests.post)

    def test_created_post_exists_in_group_list(self):
        """Пост создается в нужной группе"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        post = response.context['page_obj'][0]
        self.assertEqual(post, TaskPagesTests.post)

    def test_created_post_exists_in_profile(self):
        """Пост создается в профиле пользователя"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': TaskPagesTests.user.username}))
        post = response.context['page_obj'][0]
        self.assertEqual(post, TaskPagesTests.post)

    def test_created_post_not_exists_in_group_list(self):
        """Пост не создается в другой группе"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug2'}))
        with self.assertRaises(IndexError):
            response.context['page_obj'][0]

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={
                        'username': TaskPagesTests.user.username
                    }): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={
                        'post_id': TaskPagesTests.post.id
                    }): 'posts/post_detail.html',
            (
                reverse('posts:post_edit',
                        kwargs={'post_id': TaskPagesTests.post.id})
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        is_not_profile = response.context['is_not_profile']
        self.assertEqual(first_object, TaskPagesTests.post)
        self.assertTrue(is_not_profile, "Ошибка:эта страница"
                        "не должна быть профилем")

    def test_group_post_page_shows_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client. get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})))
        first_object = response.context['page_obj'][0]
        group = response.context['group']
        is_not_profile = response.context['is_not_profile']
        self.assertEqual(first_object, TaskPagesTests.post)
        self.assertEqual(group, TaskPagesTests.group)
        self.assertEqual(is_not_profile, True)

    def test_profile_page_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': TaskPagesTests.user.username})))
        first_object = response.context['page_obj'][0]
        task_author_0 = response.context['author']
        self.assertEqual(first_object, TaskPagesTests.post)
        self.assertEqual(task_author_0, TaskPagesTests.user)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': TaskPagesTests.post.id})))
        self.assertEqual(response.context.get('post'), TaskPagesTests.post)
        self.assertEqual(
            response.context.get('title'),
            f'Пост {TaskPagesTests.post.text[:settings.SYMBOLS_AMOUNT]}')

    def test_create_post_show_correct_context(self):
        """Форма создания поста с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)

    def test_edit_post_show_correct_context(self):
        """Форма редактирования поста с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                                kwargs={'post_id': TaskPagesTests.post.id})))
        form = response.context.get('form')
        is_edit = response.context.get('is_edit')
        self.assertIsInstance(form, PostForm)
        self.assertTrue(is_edit, "Ошибка is_edit=False"
                        ": проверь вьюшку формы.")

    def test_created_comment_exists_in_post_detail(self):
        """Комментарий создается в post_detail"""
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': TaskPagesTests.post.id})))
        comment = response.context['comments'][0]
        self.assertEqual(comment, TaskPagesTests.comment)

    def test_zcache_created_index(self):
        """Проверка сохранения кэша на главной странице"""
        response1 = self.authorized_client.get(reverse('posts:index',),)
        content_before = response1.content
        TaskPagesTests.post.delete()
        response2 = self.authorized_client.get(reverse('posts:index'))
        content_after = response2.content
        self.assertEqual(content_before, content_after)
        cache.clear()
        response3 = self.authorized_client.get(reverse('posts:index'))
        content_after_clearing_cache = response3.content
        self.assertNotEqual(content_before, content_after_clearing_cache)

    def test_404_custom_template(self):
        """404 использует кастомный шаблон"""
        response = self.authorized_client.get('/test404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_follow_unfollow(self):
        """Возможность подписываться и отписываться"""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TaskPagesTests.user2.username}))
        self.assertEqual(Follow.objects.count(), FOLLOW_FLAG)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': TaskPagesTests.user2.username}))
        self.assertEqual(Follow.objects.count(), UNFOLLOW_FLAG)
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TaskPagesTests.user.username}))
        self.assertEqual(Follow.objects.count(), UNFOLLOW_FLAG)

    def test_new_following_post(self):
        """Новая запись появляется в подписанных"""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': TaskPagesTests.user2.username}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post = response.context.get('page_obj')[0]
        self.assertTrue(post, 'В подписках нет поста')
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': TaskPagesTests.user2.username}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        context = len(response.context.get('page_obj'))
        self.assertEqual(context, UNFOLLOW_FLAG)


class PaginatorViewsTest(TestCase):
    """Тест пагинаторов"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        Post.objects.bulk_create(
            [Post(text=f'Тестовый текст{x}',
                  author=cls.user,
                  group=cls.group) for x in range(
                settings.POSTS_AMOUNT + settings.EXTRA_POSTS)]
        )

    @classmethod
    def tearDownClass(self):
        super().tearDownClass()
        for posts in Post.objects.all():
            posts.delete()

    def setUp(self):
        self.client = Client()
        self.client.force_login(PaginatorViewsTest.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_AMOUNT)

    def test_second_page_contains_two_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            settings.EXTRA_POSTS)

    def test_first_page_group_list_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_AMOUNT)

    def test_first_page_group_list_2_records(self):
        response = self.client.get(reverse('posts:group_list', kwargs={
                                   'slug': 'test-slug'}) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            settings.EXTRA_POSTS)

    def test_first_page_profile_ten_records(self):
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.username}))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.POSTS_AMOUNT)

    def test_first_page_profile_two_records(self):
        response = self.client.get(reverse('posts:profile', kwargs={
                                   'username': PaginatorViewsTest.user.username
                                   }) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']),
            settings.EXTRA_POSTS)
