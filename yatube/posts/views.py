from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post
from .utils import make_pagination

User = get_user_model()


def index(request):
    """
    Рендер главной страницы.
    (Как и во всех последующих функциях,
    где необходима пагинация -
    она реализована внутри контекста.)
    """
    post_list = Post.objects.select_related('author', 'group').all()
    context = {
        'page_obj': make_pagination(post_list, request),
        'is_not_profile': True,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Рендер страницы постов по группам"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    context = {
        'group': group,
        'page_obj': make_pagination(posts, request),
        'is_not_profile': True,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Профаил"""
    author = get_object_or_404(User, username=username)
    try:
        following = Follow.objects.get(author=author)
    except Follow.DoesNotExist:
        following = None
    context = {
        'author': author,
        'page_obj': make_pagination(author.posts.
                                    select_related('group').all(), request),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Отдельный пост"""
    post = Post.objects.select_related('author', 'group').get(pk=post_id)
    comment_form = CommentForm()
    comments = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'title': f'Пост {post.text[:settings.SYMBOLS_AMOUNT]}',
        'form': comment_form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создание поста"""
    if request.method == 'POST':
        form = PostForm(request.POST,
                        files=request.FILES or None,)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
        return render(request, 'posts/create_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.id)
    if request.method == "POST":
        form = PostForm(
            request.POST,
            files=request.FILES or None,
            instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)
        return render(request, 'posts/create_post.html',
                      {'form': form})
    form = PostForm(instance=post)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True})


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = Post.objects.get(pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Список постов по подписке"""
    posts = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': make_pagination(posts, request)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    following = get_object_or_404(User, username=username)
    if following != request.user:
        Follow.objects.get_or_create(user=request.user,
                                     author=following)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    following = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=following).delete()
    return redirect('posts:profile', username=username)
