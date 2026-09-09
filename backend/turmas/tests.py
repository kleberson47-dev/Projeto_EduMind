from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Activity, Classroom, Enrollment, Grade
from .serializers.activity_serializers import ActivitySerializer
from .serializers.grade_serializers import GradeSerializer

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


class GradeSerializerTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            email="professor_nota@teste.com",
            password="123456",
            nome="Professor Nota",
            role="professor",
        )
        self.student = User.objects.create_user(
            email="aluno_nota@teste.com",
            password="123456",
            nome="Aluno Nota",
            role="aluno",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Notas",
            descricao="Turma para testar notas.",
            codigo_acesso="NOTA98765",
            criterios_avaliacao="Avaliação.",
            regras="Regra de notas.",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.student,
            turma=self.classroom,
            ativo=True,
        )
        self.activity = Activity.objects.create(
            turma=self.classroom,
            titulo="Atividade de nota",
            descricao="Entregar a resposta.",
            tipo="atividade",
            data_entrega="2026-09-25",
            ativo=True,
        )
        self.grade = Grade.objects.create(
            aluno=self.student,
            turma=self.classroom,
            atividade=self.activity,
            valor=9.5,
            observacao="Muito bom.",
            ativo=True,
        )

    def test_grade_serializer_returns_expected_fields(self):
        serializer = GradeSerializer(instance=self.grade)

        self.assertEqual(serializer.data["valor"], "9.50")
        self.assertEqual(serializer.data["aluno"], self.student.id)
        self.assertEqual(serializer.data["turma"], self.classroom.id)
        self.assertEqual(serializer.data["atividade"], self.activity.id)


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


class ClassroomGradeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_notas@teste.com",
            password="123456",
            nome="Professor Notas",
            role="professor",
        )
        self.student = User.objects.create_user(
            email="aluno_notas@teste.com",
            password="123456",
            nome="Aluno Notas",
            role="aluno",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Notas",
            descricao="Turma para notas.",
            codigo_acesso="NOTA1234",
            criterios_avaliacao="Avaliação por prova.",
            regras="Regra de notas.",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.student,
            turma=self.classroom,
            ativo=True,
        )
        self.activity = Activity.objects.create(
            turma=self.classroom,
            titulo="Prova 1",
            descricao="Prova do módulo.",
            tipo="prova",
            data_entrega="2026-09-30",
            ativo=True,
        )

    def test_professor_can_create_grade_for_student(self):
        self.client.force_authenticate(user=self.professor)
        url = reverse("classrooms-professor-grades", args=[self.classroom.id])

        response = self.client.post(
            url,
            {
                "aluno": self.student.id,
                "atividade": self.activity.id,
                "valor": 9.5,
                "observacao": "Excelente desempenho.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["valor"], "9.50")
        self.assertEqual(response.data["aluno"], self.student.id)

    def test_student_can_list_own_grades_for_classroom(self):
        Grade.objects.create(
            aluno=self.student,
            turma=self.classroom,
            atividade=self.activity,
            valor=8.5,
            observacao="Boa nota.",
            ativo=True,
        )

        self.client.force_authenticate(user=self.student)
        url = reverse("classrooms-student-grades", args=[self.classroom.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["valor"], "8.50")
