from django.urls import path

from .views import (
    AlunoClassroomActivityListView,
    AlunoClassroomDetailView,
    AlunoClassroomGradeListView,
    AlunoClassroomListView,
    JoinClassroomView,
    ProfessorClassroomActivityListCreateView,
    ProfessorClassroomDetailView,
    ProfessorClassroomGradeListCreateView,
    ProfessorClassroomListCreateView,
)

urlpatterns = [
    path("classrooms/", ProfessorClassroomListCreateView.as_view(),
         name="classrooms-list-create"),
    path("classrooms/me/", AlunoClassroomListView.as_view(),
         name="classrooms-student-list"),
    path("classrooms/join/", JoinClassroomView.as_view(), name="classrooms-join"),
    path("classrooms/<int:id>/", AlunoClassroomDetailView.as_view(),
         name="classrooms-detail"),
    path("classrooms/professor/<int:id>/",
         ProfessorClassroomDetailView.as_view(), name="classrooms-professor-detail"),
    path("classrooms/<int:id>/activities/",
         ProfessorClassroomActivityListCreateView.as_view(), name="classrooms-professor-activities"),
    path("classrooms/<int:id>/activities/student/",
         AlunoClassroomActivityListView.as_view(), name="classrooms-student-activities"),
    path("classrooms/<int:id>/grades/",
         ProfessorClassroomGradeListCreateView.as_view(), name="classrooms-professor-grades"),
    path("classrooms/<int:id>/grades/student/",
         AlunoClassroomGradeListView.as_view(), name="classrooms-student-grades"),
]
