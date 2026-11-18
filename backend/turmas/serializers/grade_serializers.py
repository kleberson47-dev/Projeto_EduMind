from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..models import Activity, Grade

User = get_user_model()


# Serializa e valida a nota atribuída a um aluno em uma atividade da turma.
class GradeSerializer(serializers.ModelSerializer):
    aluno = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="aluno"),
    )
    turma = serializers.PrimaryKeyRelatedField(read_only=True)
    atividade = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(),
    )

    class Meta:
        model = Grade
        fields = [
            "id",
            "aluno",
            "turma",
            "atividade",
            "valor",
            "observacao",
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

    def validate(self, attrs):
        turma = self.context.get("turma")
        aluno = attrs.get("aluno", getattr(self.instance, "aluno", None))
        atividade = attrs.get(
            "atividade", getattr(self.instance, "atividade", None))
        valor = attrs.get("valor", getattr(self.instance, "valor", None))

        if turma is None:
            raise serializers.ValidationError("Turma não informada.")

        if aluno is not None and not turma.enrollments.filter(aluno=aluno, ativo=True).exists():
            raise serializers.ValidationError(
                "Aluno não está matriculado na turma."
            )

        if atividade is not None:
            if atividade.turma_id != turma.id:
                raise serializers.ValidationError(
                    "A atividade não pertence a esta turma."
                )

            if not atividade.ativo or not atividade.pontuada:
                raise serializers.ValidationError(
                    "Apenas atividades ativas e pontuadas recebem nota."
                )

            if (
                valor is not None
                and atividade.peso is not None
                and valor > atividade.peso
            ):
                raise serializers.ValidationError(
                    {"valor": f"A nota não pode ser maior que o peso da atividade ({atividade.peso})."}
                )

        if aluno is not None and atividade is not None:
            duplicadas = Grade.objects.filter(
                aluno=aluno,
                turma=turma,
                atividade=atividade,
            )
            if self.instance is not None:
                duplicadas = duplicadas.exclude(pk=self.instance.pk)

            if duplicadas.exists():
                raise serializers.ValidationError(
                    "Já existe uma nota registrada para essa atividade deste aluno."
                )

        return attrs

    def validate_valor(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "A nota não pode ser menor que zero."
            )
        if value > 10:
            raise serializers.ValidationError(
                "A nota deve estar entre 0 e 10."
            )
        return value

    def create(self, validated_data):
        turma = self.context.get("turma")
        if turma is None:
            raise serializers.ValidationError("Turma não informada.")

        validated_data["turma"] = turma
        return Grade.objects.create(**validated_data)
