import django_filters

from .models import Activity, ClassroomMaterial, Module


# Filtros explícitos de módulos; o módulo é referenciado pelo id para não consultar a tabela de módulos.
class ModuleFilter(django_filters.FilterSet):
    class Meta:
        model = Module
        fields = ["ativo"]


class ActivityFilter(django_filters.FilterSet):
    modulo = django_filters.NumberFilter(field_name="modulo_id")
    data_entrega_de = django_filters.DateFilter(
        field_name="data_entrega", lookup_expr="gte")
    data_entrega_ate = django_filters.DateFilter(
        field_name="data_entrega", lookup_expr="lte")

    class Meta:
        model = Activity
        fields = ["modulo", "tipo", "pontuada", "publicado", "ativo"]


class MaterialFilter(django_filters.FilterSet):
    modulo = django_filters.NumberFilter(field_name="modulo_id")

    class Meta:
        model = ClassroomMaterial
        fields = ["modulo", "ativo"]
