from rest_framework import serializers

from ..models import Activity


# Serializa as atividades da turma e valida o conteúdo mínimo para criação.
class ActivitySerializer(serializers.ModelSerializer):
    turma = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Activity
        fields = [
            "id",
            "turma",
            "titulo",
            "descricao",
            "tipo",
            "data_entrega",
            "ativo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "turma",
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
