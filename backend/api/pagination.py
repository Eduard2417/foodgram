from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE


class CustomPaginator(PageNumberPagination):
    '''Пагинатор для вывода 6 элементов на странице'''

    page_size = PAGE_SIZE
