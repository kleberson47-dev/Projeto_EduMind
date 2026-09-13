from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from ..models import Activity, Classroom, Grade, Lesson, LessonBlock, LessonSection
from ..serializers.activity_serializers import ActivitySerializer
from ..serializers.classroom_serializers import (
    ClassroomCreateSerializer,
    ClassroomDetailSerializer,
    ClassroomListSerializer,
    ClassroomUpdateSerializer,
)
from ..serializers.grade_serializers import GradeSerializer
from ..serializers.lesson_serializers import (
    LessonBlockSerializer,
    LessonSectionSerializer,
    LessonSerializer,
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


# Lista e cria atividades de uma turma pertencente ao professor logado.
class ProfessorClassroomActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self.request.user, "role", None) != "professor":
            return Activity.objects.none()
        return Activity.objects.filter(
            turma_id=self.kwargs.get("id"),
            turma__professor=self.request.user,
        ).order_by("data_entrega", "-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        turma = Classroom.objects.filter(
            id=self.kwargs.get("id"),
            professor=self.request.user,
        ).first()
        context["turma"] = turma
        return context

    def post(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "professor":
            return Response(
                {"detail": "Apenas professores podem criar atividades."},
                status=status.HTTP_403_FORBIDDEN,
            )

        turma = Classroom.objects.filter(
            id=kwargs.get("id"),
            professor=request.user,
        ).first()
        if turma is None:
            return Response(
                {"detail": "Turma não encontrada ou não pertence ao professor."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(turma=turma)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Lista e registra notas de alunos para uma turma pertencente ao professor logado.
class ProfessorClassroomGradeListCreateView(generics.ListCreateAPIView):
    serializer_class = GradeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self.request.user, "role", None) != "professor":
            return Grade.objects.none()
        return Grade.objects.filter(
            turma_id=self.kwargs.get("id"),
            turma__professor=self.request.user,
        ).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        turma = Classroom.objects.filter(
            id=self.kwargs.get("id"),
            professor=self.request.user,
        ).first()
        context["turma"] = turma
        return context

    def post(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "professor":
            return Response(
                {"detail": "Apenas professores podem registrar notas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        turma = Classroom.objects.filter(
            id=kwargs.get("id"),
            professor=request.user,
        ).first()
        if turma is None:
            return Response(
                {"detail": "Turma não encontrada ou não pertence ao professor."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "turma": turma},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Lista e cria aulas de uma turma pertencente ao professor logado.
class ProfessorClassroomLessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self.request.user, "role", None) != "professor":
            return Lesson.objects.none()
        return Lesson.objects.filter(
            turma_id=self.kwargs.get("id"),
            turma__professor=self.request.user,
        ).order_by("ordem", "created_at")

    def post(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "professor":
            return Response(
                {"detail": "Apenas professores podem criar aulas."},
                status=status.HTTP_403_FORBIDDEN,
            )

        turma = Classroom.objects.filter(
            id=kwargs.get("id"),
            professor=request.user,
        ).first()
        if turma is None:
            return Response(
                {"detail": "Turma não encontrada ou não pertence ao professor."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(turma=turma)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Lista e cria seções de uma aula pertencente ao professor logado.
class ProfessorLessonSectionListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self.request.user, "role", None) != "professor":
            return LessonSection.objects.none()
        return LessonSection.objects.filter(
            aula_id=self.kwargs.get("lesson_id"),
            aula__turma_id=self.kwargs.get("id"),
            aula__turma__professor=self.request.user,
        ).order_by("ordem", "created_at")

    def post(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "professor":
            return Response(
                {"detail": "Apenas professores podem criar seções."},
                status=status.HTTP_403_FORBIDDEN,
            )

        lesson = Lesson.objects.filter(
            id=kwargs.get("lesson_id"),
            turma_id=kwargs.get("id"),
            turma__professor=request.user,
        ).first()
        if lesson is None:
            return Response(
                {"detail": "Aula não encontrada ou não pertence ao professor."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(aula=lesson)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Lista e cria blocos de conteúdo dentro de uma seção pertencente ao professor logado.
class ProfessorLessonBlockListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonBlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self.request.user, "role", None) != "professor":
            return LessonBlock.objects.none()
        return LessonBlock.objects.filter(
            secao_id=self.kwargs.get("section_id"),
            secao__aula_id=self.kwargs.get("lesson_id"),
            secao__aula__turma_id=self.kwargs.get("id"),
            secao__aula__turma__professor=self.request.user,
        ).order_by("ordem", "created_at")

    def post(self, request, *args, **kwargs):
        if getattr(request.user, "role", None) != "professor":
            return Response(
                {"detail": "Apenas professores podem criar blocos."},
                status=status.HTTP_403_FORBIDDEN,
            )

        section = LessonSection.objects.filter(
            id=kwargs.get("section_id"),
            aula_id=kwargs.get("lesson_id"),
            aula__turma_id=kwargs.get("id"),
            aula__turma__professor=request.user,
        ).first()
        if section is None:
            return Response(
                {"detail": "Seção não encontrada ou não pertence ao professor."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(secao=section)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
