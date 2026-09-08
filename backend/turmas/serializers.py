from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Activity, Classroom
from .services import criar_turma_para_professor

User = get_user_model()


# Serializa os dados básicos do professor para uso em respostas de turma.
class ProfessorResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nome", "email"]
        read_only_fields = ["id", "nome", "email"]


# Valida e cria uma nova turma pelo professor autenticado.
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


# Lista as turmas em formato resumido para listagens do professor ou do aluno.
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


# Expõe os detalhes completos de uma turma para o aluno ou professor.
class ClassroomDetailSerializer(serializers.ModelSerializer):
    professor = ProfessorResumoSerializer(read_only=True)
    numero_alunos = serializers.SerializerMethodField()

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
            "numero_alunos",
            "ativo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "codigo_acesso",
            "professor",
            "numero_alunos",
            "ativo",
            "created_at",
            "updated_at",
        ]

    def get_numero_alunos(self, obj):
        return obj.enrollments.filter(ativo=True).count()


# Permite atualizar os dados básicos da turma pelo professor.
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
                "O título da atividade é obrigatório.")
        return titulo


# Valida o código de acesso usado para o aluno entrar em uma turma.
class JoinClassroomSerializer(serializers.Serializer):
    codigo_acesso = serializers.CharField(max_length=30)

    def validate_codigo_acesso(self, value):
        codigo = value.strip().upper()
        if not codigo:
            raise serializers.ValidationError("Código da turma é obrigatório.")
        return codigo
