from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import Activity, Classroom, Grade, Lesson, LessonBlock, LessonSection
from ..serializers.activity_serializers import ActivitySerializer
from ..serializers.classroom_serializers import (
    ClassroomDetailSerializer,
    ClassroomListSerializer,
    JoinClassroomSerializer,
)
from ..serializers.grade_serializers import GradeSerializer
from ..serializers.lesson_serializers import (
    LessonBlockSerializer,
    LessonSectionSerializer,
    LessonSerializer,
)
from ..services import listar_turmas_do_aluno, matricular_aluno_por_codigo


# Lista as turmas em que o aluno está matriculado e ativo.
class AlunoClassroomListView(generics.ListAPIView):
    serializer_class = ClassroomListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return listar_turmas_do_aluno(self.request.user)


# Exibe os detalhes de uma turma específica para o aluno matriculado.
class AlunoClassroomDetailView(generics.RetrieveAPIView):
    serializer_class = ClassroomDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Classroom.objects.filter(
            enrollments__aluno=self.request.user,
            enrollments__ativo=True,
            ativo=True,
        ).distinct()


# Permite que o aluno entre em uma turma usando o código de acesso.
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


# Lista as atividades de uma turma em que o aluno está matriculado.
class AlunoClassroomActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(
            turma_id=self.kwargs.get("id"),
            turma__enrollments__aluno=self.request.user,
            turma__enrollments__ativo=True,
            ativo=True,
        ).distinct().order_by("data_entrega", "-created_at")


# Lista as notas de um aluno em uma turma na qual ele está matriculado.
class AlunoClassroomGradeListView(generics.ListAPIView):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Grade.objects.filter(
            turma_id=self.kwargs.get("id"),
            aluno=self.request.user,
            turma__enrollments__aluno=self.request.user,
            turma__enrollments__ativo=True,
            ativo=True,
        ).distinct().order_by("-created_at")


# Lista as aulas de uma turma em que o aluno está matriculado.
class AlunoClassroomLessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.filter(
            turma_id=self.kwargs.get("id"),
            turma__enrollments__aluno=self.request.user,
            turma__enrollments__ativo=True,
            ativo=True,
        ).distinct().order_by("ordem", "created_at")


# Exibe uma aula específica com suas seções e blocos para o aluno matriculado.
class AlunoClassroomLessonDetailView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Lesson.objects.filter(
            turma_id=self.kwargs.get("id"),
            turma__enrollments__aluno=self.request.user,
            turma__enrollments__ativo=True,
            ativo=True,
        ).distinct()


# Lista as seções de uma aula em que o aluno está matriculado.
class AlunoLessonSectionListView(generics.ListAPIView):
    serializer_class = LessonSectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LessonSection.objects.filter(
            aula_id=self.kwargs.get("lesson_id"),
            aula__turma_id=self.kwargs.get("id"),
            aula__turma__enrollments__aluno=self.request.user,
            aula__turma__enrollments__ativo=True,
            ativo=True,
        ).distinct().order_by("ordem", "created_at")


# Lista os blocos de uma seção em que o aluno está matriculado.
class AlunoLessonBlockListView(generics.ListAPIView):
    serializer_class = LessonBlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LessonBlock.objects.filter(
            secao_id=self.kwargs.get("section_id"),
            secao__aula_id=self.kwargs.get("lesson_id"),
            secao__aula__turma_id=self.kwargs.get("id"),
            secao__aula__turma__enrollments__aluno=self.request.user,
            secao__aula__turma__enrollments__ativo=True,
            ativo=True,
        ).distinct().order_by("ordem", "created_at")
