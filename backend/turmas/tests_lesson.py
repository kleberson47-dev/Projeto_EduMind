from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Classroom, Enrollment, Lesson, LessonBlock, LessonSection
from .serializers.lesson_serializers import (
    LessonBlockSerializer,
    LessonSectionSerializer,
    LessonSerializer,
)

User = get_user_model()


class LessonSerializerTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            email="professor_lesson@teste.com",
            password="123456",
            nome="Professor Aula",
            role="professor",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Aula",
            descricao="Turma para testar aulas.",
            codigo_acesso="AULA1234",
            criterios_avaliacao="Participação e exercícios.",
            regras="Seguir os conteúdos.",
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula 1",
            descricao="Introdução ao tema.",
            ordem=1,
            ativo=True,
        )

    def test_lesson_serializer_returns_expected_fields(self):
        serializer = LessonSerializer(instance=self.lesson)

        self.assertEqual(serializer.data["titulo"], "Aula 1")
        self.assertEqual(serializer.data["turma"], self.classroom.id)
        self.assertEqual(serializer.data["ordem"], 1)
        self.assertEqual(serializer.data["ativo"], True)


class ProfessorLessonViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_aula@teste.com",
            password="123456",
            nome="Professor Aula",
            role="professor",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Conteúdo",
            descricao="Turma para conteúdo didático.",
            codigo_acesso="CONTEUDO1",
            criterios_avaliacao="Trabalhos e provas.",
            regras="Manter organização.",
            ativo=True,
        )

    def test_professor_can_create_lesson_for_classroom(self):
        self.client.force_authenticate(user=self.professor)
        url = reverse("classrooms-professor-lessons", args=[self.classroom.id])

        response = self.client.post(
            url,
            {
                "titulo": "Introdução ao módulo",
                "descricao": "Conteúdo inicial da aula.",
                "ordem": 1,
                "ativo": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["titulo"], "Introdução ao módulo")
        self.assertEqual(response.data["turma"], self.classroom.id)


class StudentLessonViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_aluno_aula@teste.com",
            password="123456",
            nome="Professor Conteúdo",
            role="professor",
        )
        self.student = User.objects.create_user(
            email="aluno_aula@teste.com",
            password="123456",
            nome="Aluno Aula",
            role="aluno",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma do Aluno",
            descricao="Aulas para alunos.",
            codigo_acesso="ALUNO2024",
            criterios_avaliacao="Participação.",
            regras="Respeitar o cronograma.",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.student,
            turma=self.classroom,
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula de revisão",
            descricao="Revisão do conteúdo.",
            ordem=1,
            ativo=True,
        )

    def test_student_can_list_lessons_for_classroom(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("classrooms-student-lessons", args=[self.classroom.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["titulo"], "Aula de revisão")


class LessonSectionSerializerTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            email="professor_secao@teste.com",
            password="123456",
            nome="Professor Seção",
            role="professor",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Seções",
            descricao="Turma para testar seções.",
            codigo_acesso="SECAO2024",
            criterios_avaliacao="Participação.",
            regras="Organizar os conteúdos.",
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula com seções",
            descricao="Aula de estudo.",
            ordem=1,
            ativo=True,
        )
        self.section = LessonSection.objects.create(
            aula=self.lesson,
            titulo="Introdução",
            descricao="Explicação inicial.",
            ordem=1,
            ativo=True,
        )

    def test_lesson_section_serializer_returns_expected_fields(self):
        serializer = LessonSectionSerializer(instance=self.section)

        self.assertEqual(serializer.data["titulo"], "Introdução")
        self.assertEqual(serializer.data["aula"], self.lesson.id)
        self.assertEqual(serializer.data["ordem"], 1)
        self.assertEqual(serializer.data["ativo"], True)


class LessonBlockSerializerTests(TestCase):
    def setUp(self):
        self.professor = User.objects.create_user(
            email="professor_bloco@teste.com",
            password="123456",
            nome="Professor Bloco",
            role="professor",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Blocos",
            descricao="Turma para testar blocos.",
            codigo_acesso="BLOCO2024",
            criterios_avaliacao="Conteúdo e exercícios.",
            regras="Respeitar a ordem.",
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula com blocos",
            descricao="Conteúdo em blocos.",
            ordem=1,
            ativo=True,
        )
        self.section = LessonSection.objects.create(
            aula=self.lesson,
            titulo="Desenvolvimento",
            descricao="Parte principal da aula.",
            ordem=1,
            ativo=True,
        )
        self.block = LessonBlock.objects.create(
            secao=self.section,
            tipo=LessonBlock.TIPO_TEXTO,
            titulo="Texto principal",
            conteudo="Este é o conteúdo do bloco.",
            ordem=1,
            ativo=True,
        )

    def test_lesson_block_serializer_returns_expected_fields(self):
        serializer = LessonBlockSerializer(instance=self.block)

        self.assertEqual(serializer.data["titulo"], "Texto principal")
        self.assertEqual(serializer.data["tipo"], LessonBlock.TIPO_TEXTO)
        self.assertEqual(serializer.data["secao"], self.section.id)
        self.assertEqual(serializer.data["ordem"], 1)
        self.assertEqual(
            serializer.data["conteudo"], "Este é o conteúdo do bloco.")


class StudentSectionViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_secao_aluno@teste.com",
            password="123456",
            nome="Professor Seção Aluno",
            role="professor",
        )
        self.student = User.objects.create_user(
            email="aluno_secao@teste.com",
            password="123456",
            nome="Aluno Seção",
            role="aluno",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Seções Aluno",
            descricao="Turma para testar seções do aluno.",
            codigo_acesso="SECALUNO1",
            criterios_avaliacao="Participação.",
            regras="Organização do conteúdo.",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.student,
            turma=self.classroom,
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula de estrutura",
            descricao="Aula para testar seções.",
            ordem=1,
            ativo=True,
        )
        LessonSection.objects.create(
            aula=self.lesson,
            titulo="Introdução teórica",
            descricao="Base do conteúdo.",
            ordem=1,
            ativo=True,
        )

    def test_student_can_list_sections_for_lesson(self):
        self.client.force_authenticate(user=self.student)
        url = reverse(
            "classrooms-student-sections",
            args=[self.classroom.id, self.lesson.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["titulo"], "Introdução teórica")


class StudentBlockViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_bloco_aluno@teste.com",
            password="123456",
            nome="Professor Bloco Aluno",
            role="professor",
        )
        self.student = User.objects.create_user(
            email="aluno_bloco@teste.com",
            password="123456",
            nome="Aluno Bloco",
            role="aluno",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Blocos Aluno",
            descricao="Turma para testar blocos do aluno.",
            codigo_acesso="BLOCOALUNO1",
            criterios_avaliacao="Conteúdo e exercícios.",
            regras="Ordem do material.",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.student,
            turma=self.classroom,
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula de conteúdos",
            descricao="Aula para testar blocos.",
            ordem=1,
            ativo=True,
        )
        self.section = LessonSection.objects.create(
            aula=self.lesson,
            titulo="Desenvolvimento",
            descricao="Parte principal.",
            ordem=1,
            ativo=True,
        )
        LessonBlock.objects.create(
            secao=self.section,
            tipo=LessonBlock.TIPO_TEXTO,
            titulo="Texto explicativo",
            conteudo="Este bloco é legível pelo aluno.",
            ordem=1,
            ativo=True,
        )

    def test_student_can_list_blocks_for_section(self):
        self.client.force_authenticate(user=self.student)
        url = reverse(
            "classrooms-student-blocks",
            args=[self.classroom.id, self.lesson.id, self.section.id],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["titulo"], "Texto explicativo")


class ProfessorLessonSectionViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_secao_view@teste.com",
            password="123456",
            nome="Professor Seção View",
            role="professor",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Seções API",
            descricao="Turma para testar seções via API.",
            codigo_acesso="SECAOAPI1",
            criterios_avaliacao="Participação.",
            regras="Manter a ordem.",
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula de estrutura",
            descricao="Aula para testar seções.",
            ordem=1,
            ativo=True,
        )

    def test_professor_can_create_section_for_lesson(self):
        self.client.force_authenticate(user=self.professor)
        url = reverse("classrooms-professor-sections",
                      args=[self.classroom.id, self.lesson.id])

        response = self.client.post(
            url,
            {
                "titulo": "Introdução teórica",
                "descricao": "Conceptos iniciais da aula.",
                "ordem": 1,
                "ativo": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["titulo"], "Introdução teórica")
        self.assertEqual(response.data["aula"], self.lesson.id)


class ProfessorLessonBlockViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = User.objects.create_user(
            email="professor_bloco_view@teste.com",
            password="123456",
            nome="Professor Bloco View",
            role="professor",
        )
        self.classroom = Classroom.objects.create(
            professor=self.professor,
            nome="Turma de Blocos API",
            descricao="Turma para testar blocos via API.",
            codigo_acesso="BLOCOAPI1",
            criterios_avaliacao="Conteúdo e exercícios.",
            regras="Manter coerência.",
            ativo=True,
        )
        self.lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula de conteúdos",
            descricao="Aula para testar blocos.",
            ordem=1,
            ativo=True,
        )
        self.section = LessonSection.objects.create(
            aula=self.lesson,
            titulo="Desenvolvimento",
            descricao="Parte principal.",
            ordem=1,
            ativo=True,
        )

    def test_professor_can_create_block_for_section(self):
        self.client.force_authenticate(user=self.professor)
        url = reverse(
            "classrooms-professor-blocks",
            args=[self.classroom.id, self.lesson.id, self.section.id],
        )

        response = self.client.post(
            url,
            {
                "tipo": LessonBlock.TIPO_TEXTO,
                "titulo": "Texto explicativo",
                "conteudo": "Este bloco contém a explicação principal.",
                "ordem": 1,
                "ativo": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["titulo"], "Texto explicativo")
        self.assertEqual(response.data["secao"], self.section.id)
        self.assertEqual(response.data["tipo"], LessonBlock.TIPO_TEXTO)
