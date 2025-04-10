from rest_framework.pagination import PageNumberPagination

from .constants import PAGE_SIZE


class CustomPaginator(PageNumberPagination):
    page_size = PAGE_SIZE
