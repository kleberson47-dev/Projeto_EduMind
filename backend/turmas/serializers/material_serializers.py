import os

from rest_framework import serializers

from ..models import ClassroomMaterial
from .common_serializers import ModuloDaTurmaField, validar_arquivo

MAX_SIZE_MATERIAL_MB = 20
EXTENSOES_MATERIAL = {
    "pdf",
    "doc",
    "docx",
    "xls",
    "xlsx",
    "csv",
    "ppt",
    "pptx",
    "txt",
    "png",
    "jpg",
    "jpeg",
}


# Serializa o material complementar; o arquivo é privado e só é baixado por endpoint autenticado.
class ClassroomMaterialSerializer(serializers.ModelSerializer):
    turma = serializers.PrimaryKeyRelatedField(read_only=True)
    modulo = ModuloDaTurmaField(required=False, allow_null=True)
    arquivo = serializers.FileField(write_only=True)
    # No multipart, um booleano ausente seria lido como False; o default evita criar materiais inativos.
    ativo = serializers.BooleanField(default=True)
    arquivo_nome = serializers.SerializerMethodField()

    class Meta:
        model = ClassroomMaterial
        fields = [
            "id",
            "turma",
            "modulo",
            "titulo",
            "descricao",
            "arquivo",
            "arquivo_nome",
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

    def get_arquivo_nome(self, obj):
        return os.path.basename(obj.arquivo.name)

    def validate_titulo(self, value):
        titulo = value.strip()
        if not titulo:
            raise serializers.ValidationError(
                "O título do material é obrigatório.")
        return titulo

    def validate_arquivo(self, value):
        return validar_arquivo(value, EXTENSOES_MATERIAL, MAX_SIZE_MATERIAL_MB)
