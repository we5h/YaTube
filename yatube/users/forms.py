from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


#  создадим собственный класс для формы регистрации
#  сделаем его наследником предустановленного класса UserCreationForm
class CreationForm(UserCreationForm):
    """Форма для создания пользователя"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'email', 'password1', 'password2',)
