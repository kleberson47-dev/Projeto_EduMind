from django.urls import path

from .views import ClassroomDetailView, ClassroomListView, JoinClassroomView

urlpatterns = [
    path("classrooms/", ClassroomListView.as_view(), name="classrooms-list"),
    path("classrooms/join/", JoinClassroomView.as_view(), name="classrooms-join"),
    path("classrooms/<int:id>/", ClassroomDetailView.as_view(),
         name="classrooms-detail"),
]
