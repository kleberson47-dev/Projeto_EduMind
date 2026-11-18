from rest_framework import serializers

from ..models import Activity
from ..services_atividades import atualizar_atividade, criar_atividade
from .common_serializers import ModuloDaTurmaField, traduzir_erros_de_dominio


# Serializa as atividades da turma; peso, publicação e regras de criação ficam sob responsabilidade dos services.
class ActivitySerializer(serializers.ModelSerializer):
    turma = serializers.PrimaryKeyRelatedField(read_only=True)
    modulo = ModuloDaTurmaField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "turma",
            "modulo",
            "titulo",
            "descricao",
            "tipo",
            "pontuada",
            "peso",
            "data_inicio",
            "data_entrega",
            "publicado",
            "max_revisoes",
            "quantidade_sorteio",
            "modo_recuperacao",
            "ativo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "turma",
            "publicado",
            "created_at",
            "updated_at",
        ]

    def validate_titulo(self, value):
        titulo = value.strip()
        if not titulo:
            raise serializers.ValidationError(
                "O título da atividade é obrigatório."
            )
        return titulo

    def validate(self, attrs):
        modulo = attrs.get("modulo")
        if (
            self.instance is not None
            and modulo is not None
            and modulo.pk != self.instance.modulo_id
        ):
            raise serializers.ValidationError(
                {"modulo": "O módulo da atividade não pode ser alterado."}
            )
        return attrs

    def create(self, validated_data):
        turma = self.context.get("turma")
        if turma is None:
            raise serializers.ValidationError("Turma não informada.")

        modulo = validated_data.pop("modulo")
        with traduzir_erros_de_dominio():
            return criar_atividade(turma, modulo, validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("modulo", None)
        with traduzir_erros_de_dominio():
            return atualizar_atividade(instance, validated_data)
