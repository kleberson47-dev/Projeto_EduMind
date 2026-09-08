from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Classroom, Enrollment

User = get_user_model()


class StudentClassroomDetailTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor@teste.com",
            password="123456",
            nome="Professor Teste",
            role="professor",
        )
        self.student = User.objects.create_user(
            email="aluno@teste.com",
            password="123456",
            nome="Aluno Teste",
            role="aluno",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Python",
            descricao="Aprendendo Python.",
            codigo_acesso="ABC12345",
            criterios_avaliacao="Tarefas e prova.",
            regras="Entrar no horário.",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.student, turma=self.classroom, ativo=True)

    def test_student_can_view_classroom_detail_with_basic_data(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("classrooms-detail", args=[self.classroom.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.classroom.id)
        self.assertEqual(response.data["nome"], "Turma de Python")
        self.assertEqual(response.data["descricao"], "Aprendendo Python.")
        self.assertEqual(response.data["professor"]["nome"], "Professor Teste")
        self.assertEqual(response.data["numero_alunos"], 1)
