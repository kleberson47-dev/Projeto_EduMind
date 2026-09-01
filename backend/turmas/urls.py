from django.urls import path

from .views import (
    AlunoClassroomDetailView,
    AlunoClassroomListView,
    JoinClassroomView,
    ProfessorClassroomDetailView,
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
]
