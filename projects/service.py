from django.core.paginator import Paginator


def get_paginated_queryset(queryset, request, per_page=12):
    """
    Args:
        queryset: QuerySet для пагинации
        request: Request объект
        per_page: Количество элементов на странице (по умолчанию 12)
    
    Returns:
        Page object с пагинированными данными
    """
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
