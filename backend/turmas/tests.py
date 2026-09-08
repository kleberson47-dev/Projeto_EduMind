from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Activity, Classroom, Enrollment
from .serializers import ActivitySerializer

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


class ActivitySerializerTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            email="professor_atividade@teste.com",
            password="123456",
            nome="Professor Atividade",
            role="professor",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Atividades",
            descricao="Turma para testar atividades.",
            codigo_acesso="ATV12345",
            criterios_avaliacao="Teste.",
            regras="Regra de teste.",
            ativo=True,
        )
        self.activity = Activity.objects.create(
            turma=self.classroom,
            titulo="Atividade 1",
            descricao="Descreva sua resposta.",
            tipo="atividade",
            data_entrega="2026-09-15",
            ativo=True,
        )

    def test_activity_serializer_returns_expected_fields(self):
        serializer = ActivitySerializer(instance=self.activity)

        self.assertEqual(serializer.data["titulo"], "Atividade 1")
        self.assertEqual(serializer.data["tipo"], "atividade")
        self.assertEqual(serializer.data["turma"], self.classroom.id)
        self.assertEqual(serializer.data["ativo"], True)


class ClassroomActivityViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_atividades@teste.com",
            password="123456",
            nome="Professor Atividades",
            role="professor",
        )
        self.student = User.objects.create_user(
            email="aluno_atividades@teste.com",
            password="123456",
            nome="Aluno Atividades",
            role="aluno",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Atividades",
            descricao="Atividades do aluno.",
            codigo_acesso="ACT45678",
            criterios_avaliacao="Participação.",
            regras="Sem atraso.",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.student,
            turma=self.classroom,
            ativo=True,
        )
        self.activity = Activity.objects.create(
            turma=self.classroom,
            titulo="Atividade inicial",
            descricao="Entregar no prazo.",
            tipo="atividade",
            data_entrega="2026-09-20",
            ativo=True,
        )

    def test_professor_can_create_activity_for_classroom(self):
        self.client.force_authenticate(user=self.professor)
        url = reverse("classrooms-professor-activities",
                      args=[self.classroom.id])

        response = self.client.post(
            url,
            {
                "titulo": "Nova atividade",
                "descricao": "Fazer os exercícios.",
                "tipo": "atividade",
                "data_entrega": "2026-09-25",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["titulo"], "Nova atividade")
        self.assertEqual(response.data["turma"], self.classroom.id)

    def test_student_can_list_activities_for_classroom(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("classrooms-student-activities",
                      args=[self.classroom.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["titulo"], "Atividade inicial")
