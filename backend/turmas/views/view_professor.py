from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import Classroom
from ..serializers import (
    ClassroomCreateSerializer,
    ClassroomDetailSerializer,
    ClassroomListSerializer,
    ClassroomUpdateSerializer,
)
from ..services import listar_turmas_do_aluno


# Lista as turmas do professor e também permite criar uma nova turma.
class ProfessorClassroomListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ClassroomCreateSerializer
        return ClassroomListSerializer

    def get_queryset(self):
        if getattr(self.request.user, "role", None) == "professor":
            return Classroom.objects.filter(professor=self.request.user).order_by("nome")
        return listar_turmas_do_aluno(self.request.user)

    def perform_create(self, serializer):
        if getattr(self.request.user, "role", None) != "professor":
            raise ValidationError("Apenas professores podem criar turmas.")
        serializer.save()

    def post(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "professor":
            return Response(
                {"detail": "Apenas professores podem criar turmas."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().post(request, *args, **kwargs)


# Exibe e atualiza os dados básicos de uma turma específica pertencente ao professor.
class ProfessorClassroomDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return ClassroomUpdateSerializer
        return ClassroomDetailSerializer

    def get_queryset(self):
        if getattr(self.request.user, "role", None) == "professor":
            return Classroom.objects.filter(professor=self.request.user).distinct()
        return Classroom.objects.none()

    def update(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "professor":
            return Response(
                {"detail": "Apenas professores podem atualizar turmas."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)
