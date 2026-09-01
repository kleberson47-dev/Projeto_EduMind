from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Classroom
from .services import criar_turma_para_professor

User = get_user_model()


class ProfessorResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nome", "email"]
        read_only_fields = ["id", "nome", "email"]


class ClassroomCreateSerializer(serializers.ModelSerializer):
    professor = ProfessorResumoSerializer(read_only=True)

    class Meta:
        model = Classroom
        fields = [
            "id",
            "nome",
            "descricao",
            "criterios_avaliacao",
            "regras",
            "codigo_acesso",
            "professor",
            "ativo",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "codigo_acesso",
            "professor",
            "ativo",
            "created_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            raise serializers.ValidationError("Autenticação necessária.")

        return criar_turma_para_professor(
            professor=request.user,
            nome=validated_data.get("nome", ""),
            descricao=validated_data.get("descricao", ""),
            criterios_avaliacao=validated_data.get("criterios_avaliacao", ""),
            regras=validated_data.get("regras", ""),
        )


class ClassroomListSerializer(serializers.ModelSerializer):
    professor_nome = serializers.SerializerMethodField()

    class Meta:
        model = Classroom
        fields = [
            "id",
            "nome",
            "descricao",
            "codigo_acesso",
            "professor_nome",
            "ativo",
        ]
        read_only_fields = ["id", "codigo_acesso", "professor_nome", "ativo"]

    def get_professor_nome(self, obj):
        return obj.professor.nome


class ClassroomDetailSerializer(serializers.ModelSerializer):
    professor = ProfessorResumoSerializer(read_only=True)

    class Meta:
        model = Classroom
        fields = [
            "id",
            "nome",
            "descricao",
            "codigo_acesso",
            "criterios_avaliacao",
            "regras",
            "professor",
            "ativo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "codigo_acesso",
            "professor",
            "ativo",
            "created_at",
            "updated_at",
        ]


class ClassroomUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = [
            "nome",
            "descricao",
            "criterios_avaliacao",
            "regras",
            "ativo",
        ]

    def validate_nome(self, value):
        nome = value.strip()
        if not nome:
            raise serializers.ValidationError("O nome da turma é obrigatório.")
        return nome


class JoinClassroomSerializer(serializers.Serializer):
    codigo_acesso = serializers.CharField(max_length=30)

    def validate_codigo_acesso(self, value):
        codigo = value.strip().upper()
        if not codigo:
            raise serializers.ValidationError("Código da turma é obrigatório.")
        return codigo
