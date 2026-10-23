from django.urls import path

from .views import (
    AlunoClassroomActivityListView,
    AlunoClassroomDetailView,
    AlunoClassroomGradeListView,
    AlunoClassroomLessonDetailView,
    AlunoClassroomLessonListView,
    AlunoClassroomListView,
    AlunoLessonBlockListView,
    AlunoLessonSectionListView,
    JoinClassroomView,
    ProfessorClassroomActivityListCreateView,
    ProfessorClassroomDetailView,
    ProfessorClassroomGradeListCreateView,
    ProfessorLessonDetailUpdateView,
    ProfessorClassroomLessonListCreateView,
    ProfessorClassroomListCreateView,
    ProfessorLessonBlockDetailUpdateView,
    ProfessorLessonBlockListCreateView,
    ProfessorLessonSectionDetailUpdateView,
    ProfessorLessonSectionListCreateView,
)

urlpatterns = [
    # Lista e cria turmas do professor; também expõe o endpoint de cadastro de turma.
    path("classrooms/", ProfessorClassroomListCreateView.as_view(),
         name="classrooms-list-create"),
    # Lista as turmas em que o aluno está matriculado.
    path("classrooms/me/", AlunoClassroomListView.as_view(),
         name="classrooms-student-list"),
    # Permite que um aluno entre em uma turma usando o código de acesso.
    path("classrooms/join/", JoinClassroomView.as_view(), name="classrooms-join"),
    # Detalha uma turma específica para consulta do aluno.
    path("classrooms/<int:id>/", AlunoClassroomDetailView.as_view(),
         name="classrooms-detail"),
    # Detalha e atualiza uma turma pertencente ao professor logado.
    path("classrooms/professor/<int:id>/",
         ProfessorClassroomDetailView.as_view(), name="classrooms-professor-detail"),
    # Lista e cria atividades da turma do professor.
    path("classrooms/<int:id>/activities/",
         ProfessorClassroomActivityListCreateView.as_view(), name="classrooms-professor-activities"),
    # Lista as atividades visíveis ao aluno dentro da turma.
    path("classrooms/<int:id>/activities/student/",
         AlunoClassroomActivityListView.as_view(), name="classrooms-student-activities"),
    # Lista e cria aulas de uma turma do professor.
    path("classrooms/<int:id>/lessons/",
         ProfessorClassroomLessonListCreateView.as_view(), name="classrooms-professor-lessons"),
    # Detalha e atualiza uma aula específica do professor.
    path("classrooms/<int:id>/lessons/professor/<int:lesson_id>/",
         ProfessorLessonDetailUpdateView.as_view(), name="classrooms-professor-lesson-detail"),
    # Lista e cria seções dentro de uma aula do professor.
    path("classrooms/<int:id>/lessons/<int:lesson_id>/sections/",
         ProfessorLessonSectionListCreateView.as_view(), name="classrooms-professor-sections"),
    # Detalha e atualiza uma seção específica de uma aula do professor.
    path("classrooms/<int:id>/lessons/<int:lesson_id>/sections/<int:section_id>/",
         ProfessorLessonSectionDetailUpdateView.as_view(), name="classrooms-professor-section-detail"),
    # Lista e cria blocos de conteúdo dentro de uma seção do professor.
    path("classrooms/<int:id>/lessons/<int:lesson_id>/sections/<int:section_id>/blocks/",
         ProfessorLessonBlockListCreateView.as_view(), name="classrooms-professor-blocks"),
    # Detalha e atualiza um bloco de conteúdo específico do professor.
    path("classrooms/<int:id>/lessons/<int:lesson_id>/sections/<int:section_id>/blocks/<int:block_id>/",
         ProfessorLessonBlockDetailUpdateView.as_view(), name="classrooms-professor-block-detail"),
    # Lista as aulas disponíveis para o aluno dentro da turma.
    path("classrooms/<int:id>/lessons/student/",
         AlunoClassroomLessonListView.as_view(), name="classrooms-student-lessons"),
    # Lista as seções de uma aula para o aluno visualizar o conteúdo.
    path("classrooms/<int:id>/lessons/<int:lesson_id>/sections/student/",
         AlunoLessonSectionListView.as_view(), name="classrooms-student-sections"),
    # Lista os blocos de uma seção para o aluno consumir o material didático.
    path("classrooms/<int:id>/lessons/<int:lesson_id>/sections/<int:section_id>/blocks/student/",
         AlunoLessonBlockListView.as_view(), name="classrooms-student-blocks"),
    # Detalha uma aula específica para leitura pelo aluno.
    path("classrooms/<int:id>/lessons/<int:lesson_id>/",
         AlunoClassroomLessonDetailView.as_view(), name="classrooms-student-lesson-detail"),
    # Lista e registra notas de uma turma pelo professor.
    path("classrooms/<int:id>/grades/",
         ProfessorClassroomGradeListCreateView.as_view(), name="classrooms-professor-grades"),
    # Lista as notas do aluno dentro da turma.
    path("classrooms/<int:id>/grades/student/",
         AlunoClassroomGradeListView.as_view(), name="classrooms-student-grades"),
]
