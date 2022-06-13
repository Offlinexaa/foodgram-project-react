from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """
    Паджинатор с определением атрибута 'page_size_query_param' из фронтенда
    для вывода запрошенного количества страниц.
    """
    page_size_query_param = 'limit'
