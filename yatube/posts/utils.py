from django.conf import settings
from django.core.paginator import Paginator


def make_pagination(object, request):
    """Функция для создания постраничной пагинации"""
    paginator = Paginator(object, settings.POSTS_AMOUNT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
