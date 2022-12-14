from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    """Группы"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class Post(CreatedModel):
    """Посты"""
    text = models.TextField(max_length=4000, verbose_name="Текст поста")
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name="Группа"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text[:settings.SYMBOLS_AMOUNT]

    class Meta:
        verbose_name = "Пост автора"
        verbose_name_plural = "Посты авторов"
        ordering = ['-pub_date']


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(max_length=1000, verbose_name="Текст комментария")


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        null=True
    )
