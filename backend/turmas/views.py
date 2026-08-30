from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Classroom
from .services import listar_turmas_do_aluno, matricular_aluno_por_codigo
from .serializers import (
    ClassroomCreateSerializer,
    ClassroomDetailSerializer,
    ClassroomListSerializer,
    JoinClassroomSerializer,
)


class ClassroomListView(generics.ListCreateAPIView):
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
        serializer.save()


class ClassroomDetailView(generics.RetrieveAPIView):
    serializer_class = ClassroomDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        if getattr(self.request.user, "role", None) == "professor":
            return Classroom.objects.filter(professor=self.request.user).distinct()

        return Classroom.objects.filter(
            enrollments__aluno=self.request.user,
            enrollments__ativo=True,
            ativo=True,
        ).distinct()


class JoinClassroomView(generics.GenericAPIView):
    serializer_class = JoinClassroomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        codigo_acesso = serializer.validated_data["codigo_acesso"]

        try:
            matricula = matricular_aluno_por_codigo(
                request.user, codigo_acesso)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Matrícula realizada com sucesso.",
                "classroom_id": matricula.turma.id,
                "classroom_name": matricula.turma.nome,
            },
            status=status.HTTP_201_CREATED,
        )
