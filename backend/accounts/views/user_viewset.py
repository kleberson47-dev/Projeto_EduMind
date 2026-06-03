import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import User
from ..serializers import UserSerializer


# Paginacao padrao para listagens de usuarios.
class PaginacaoUsuario(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# Filtros permitidos para consultas de usuarios.
class FiltroUsuario(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name="role")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = User
        fields = ["role", "is_active"]


# CRUD completo de usuarios com filtros, busca e ordenacao.
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaginacaoUsuario
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = FiltroUsuario
    search_fields = ["nome", "email"]
    ordering_fields = ["created_at", "nome", "email"]
    ordering = ["-created_at"]

    @action(methods=["get"], detail=False, url_path="me")
    def me(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(methods=["post"], detail=False, url_path="criar_usuario",
            permission_classes=[permissions.AllowAny])
    def criar_usuario(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @action(methods=["put", "patch"], detail=True, url_path="editar_usuario")
    def editar_usuario(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @action(methods=["delete"], detail=True, url_path="excluir_usuario")
    def excluir_usuario(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
