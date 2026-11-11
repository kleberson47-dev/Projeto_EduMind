from rest_framework.pagination import PageNumberPagination


# Paginação aplicada por view (pagination_class) para não alterar as listas já consumidas pelo frontend.
class PaginacaoPadrao(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
