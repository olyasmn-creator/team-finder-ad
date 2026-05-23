from django.core.paginator import Paginator

from .constants import USERS_PER_PAGE


def get_paginated_queryset(queryset, request, per_page=None):
    """
    Возвращает пагинированный queryset.
    
    Args:
        queryset: QuerySet для пагинации
        request: Request объект
        per_page: Количество элементов на странице (по умолчанию из константы)
    
    Returns:
        Page object с пагинированными данными
    """
    if per_page is None:
        per_page = USERS_PER_PAGE
    
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
