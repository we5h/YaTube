from django.contrib.auth.views import (PasswordChangeView,
                                       PasswordResetConfirmView,
                                       PasswordResetView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Регистрация пользователя"""
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class MyPasswordChangeView(PasswordChangeView):
    """Смена пароля(переопределил класс для редайректа)"""
    success_url = reverse_lazy('users:password_change_done')


class MyPasswordResetView(PasswordResetView):
    """Сброс пароля(переопределил класс для редайректа)"""
    success_url = reverse_lazy('users:password_reset_done')


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    """Подтверждение сброса пароля(переопределил класс для редайректа)"""
    success_url = reverse_lazy('users:password_reset_complete')
