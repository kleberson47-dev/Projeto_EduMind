from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


# Serializa os dados básicos do professor para uso em respostas de turma.
class ProfessorResumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "nome", "email"]
        read_only_fields = ["id", "nome", "email"]
