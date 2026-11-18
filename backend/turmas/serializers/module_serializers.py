from decimal import Decimal

from rest_framework import serializers

from ..models import Module
from ..services_atividades import criar_modulo
from .common_serializers import traduzir_erros_de_dominio


# Serializa o módulo da turma; a soma de pesos vem anotada na consulta da view para evitar N+1.
class ModuleSerializer(serializers.ModelSerializer):
    turma = serializers.PrimaryKeyRelatedField(read_only=True)
    pesos_distribuidos = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            "id",
            "turma",
            "nome",
            "ordem",
            "modo_distribuicao",
            "pesos_distribuidos",
            "ativo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "turma",
            "ordem",
            "modo_distribuicao",
            "ativo",
            "created_at",
            "updated_at",
        ]

    def get_pesos_distribuidos(self, obj):
        total = getattr(obj, "pesos_total", None) or Decimal("0")
        return f"{total:.2f}"

    def validate_nome(self, value):
        nome = value.strip()
        if not nome:
            raise serializers.ValidationError(
                "O nome do módulo é obrigatório.")
        return nome

    def create(self, validated_data):
        turma = self.context.get("turma")
        if turma is None:
            raise serializers.ValidationError("Turma não informada.")

        with traduzir_erros_de_dominio():
            return criar_modulo(turma, validated_data["nome"])


# Valida o critério de distribuição de pontos escolhido pelo professor para o módulo.
class DefinirModoDistribuicaoSerializer(serializers.Serializer):
    modo = serializers.ChoiceField(choices=Module.MODOS_DISTRIBUICAO)
