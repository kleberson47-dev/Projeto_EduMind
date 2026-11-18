import os
from contextlib import contextmanager

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from ..models import Module

User = get_user_model()


# Converte os erros de regra de negócio dos services em erros de API (HTTP 400).
@contextmanager
def traduzir_erros_de_dominio():
    try:
        yield
    except DjangoValidationError as exc:
        raise serializers.ValidationError(
            serializers.as_serializer_error(exc)) from exc


# Valida extensão e tamanho de um arquivo enviado; reutilizável por materiais e entregas.
def validar_arquivo(arquivo, extensoes, tamanho_maximo_mb):
    extensao = os.path.splitext(arquivo.name)[1].lstrip(".").lower()
    if extensao not in extensoes:
        raise serializers.ValidationError(
            "Formato de arquivo inválido. Use: "
            + ", ".join(sorted(extensoes)).upper()
            + "."
        )

    if arquivo.size > tamanho_maximo_mb * 1024 * 1024:
        raise serializers.ValidationError(
            f"O arquivo deve ter no máximo {tamanho_maximo_mb} MB."
        )

    return arquivo


# Aceita apenas módulos ativos da turma da requisição, evitando vincular itens a módulos de outras turmas.
class ModuloDaTurmaField(serializers.PrimaryKeyRelatedField):
    def _turma_id(self):
        turma = self.context.get("turma")
        if turma is not None:
            return turma.id

        view = self.context.get("view")
        return getattr(view, "kwargs", {}).get("id")

    def get_queryset(self):
        turma_id = self._turma_id()
        if turma_id is None:
            return Module.objects.none()
        return Module.objects.filter(turma_id=turma_id, ativo=True)


# Serializa os dados básicos do professor para uso em respostas de turma.
class ProfessorResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nome", "email"]
        read_only_fields = ["id", "nome", "email"]
