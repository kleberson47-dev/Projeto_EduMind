from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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

    def test_professor_can_update_lesson_for_classroom(self):
        lesson = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula inicial",
            descricao="Descrição inicial.",
            ordem=1,
            ativo=True,
        )
        self.client.force_authenticate(user=self.professor)
        url = reverse(
            "classrooms-professor-lesson-detail",
            args=[self.classroom.id, lesson.id],
        )

        response = self.client.patch(
            url,
            {
                "titulo": "Aula atualizada",
                "descricao": "Descrição atualizada.",
                "ordem": 2,
                "ativo": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["titulo"], "Aula atualizada")
        self.assertEqual(response.data["ordem"], 2)
        self.assertFalse(response.data["ativo"])

    def test_professor_can_reorder_lessons_for_classroom(self):
        lesson_1 = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula 1",
            descricao="Primeira aula.",
            ordem=1,
            ativo=True,
        )
        lesson_2 = Lesson.objects.create(
            turma=self.classroom,
            titulo="Aula 2",
            descricao="Segunda aula.",
            ordem=2,
            ativo=True,
        )

        self.client.force_authenticate(user=self.professor)
        url = reverse(
            "classrooms-professor-lesson-detail",
            args=[self.classroom.id, lesson_2.id],
        )

        response = self.client.patch(url, {"ordem": 1}, format="json")

        self.assertEqual(response.status_code, 200)
        lesson_1.refresh_from_db()
        lesson_2.refresh_from_db()
        self.assertEqual(lesson_1.ordem, 2)
        self.assertEqual(lesson_2.ordem, 1)


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

    def test_lesson_block_serializer_accepts_image_upload(self):
        imagem_path = r"C:\Users\Kleberson\AppData\Roaming\Code\agentSessionData\041993dd-6dba-4c4b-b06f-511401c3df8b\attachments\d8b071a5-5349-439a-9951-cee1b3ae0918\teste.png"
        with open(imagem_path, "rb") as arquivo:
            imagem = SimpleUploadedFile(
                "teste.png",
                arquivo.read(),
                content_type="image/png",
            )

        serializer = LessonBlockSerializer(
            data={
                "tipo": LessonBlock.TIPO_IMAGEM,
                "titulo": "Imagem da aula",
                "arquivo_imagem": imagem,
                "ordem": 2,
                "ativo": True,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        bloco = serializer.save(secao=self.section)
        self.assertTrue(bloco.arquivo_imagem)
        self.assertEqual(bloco.tipo, LessonBlock.TIPO_IMAGEM)

    def test_lesson_block_serializer_accepts_video_upload_and_video_url(self):
        video_path = r"C:\Users\Kleberson\Desktop\Programação\meus_projetos\Projeto_EduMind\video_teste.mp4"
        with open(video_path, "rb") as arquivo:
            video_upload = SimpleUploadedFile(
                "video_teste.mp4",
                arquivo.read(),
                content_type="video/mp4",
            )

        serializer_upload = LessonBlockSerializer(
            data={
                "tipo": LessonBlock.TIPO_VIDEO,
                "titulo": "Vídeo em upload",
                "arquivo_video": video_upload,
                "ordem": 2,
                "ativo": True,
            }
        )
        self.assertTrue(serializer_upload.is_valid(), serializer_upload.errors)
        bloco_upload = serializer_upload.save(secao=self.section)
        self.assertTrue(bloco_upload.arquivo_video)

        serializer_url = LessonBlockSerializer(
            data={
                "tipo": LessonBlock.TIPO_VIDEO,
                "titulo": "Vídeo em link",
                "url_video": "https://example.com/video.mp4",
                "ordem": 3,
                "ativo": True,
            }
        )
        self.assertTrue(serializer_url.is_valid(), serializer_url.errors)
        bloco_url = serializer_url.save(secao=self.section)
        self.assertEqual(bloco_url.url_video, "https://example.com/video.mp4")

    def test_lesson_block_serializer_rejects_video_with_file_and_url(self):
        video_path = r"C:\Users\Kleberson\Desktop\Programação\meus_projetos\Projeto_EduMind\video_teste.mp4"
        with open(video_path, "rb") as arquivo:
            video = SimpleUploadedFile(
                "video_teste.mp4",
                arquivo.read(),
                content_type="video/mp4",
            )
        serializer = LessonBlockSerializer(
            data={
                "tipo": LessonBlock.TIPO_VIDEO,
                "titulo": "Vídeo inválido",
                "arquivo_video": video,
                "url_video": "https://example.com/video.mp4",
                "ordem": 2,
                "ativo": True,
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_lesson_block_serializer_updates_video_file_when_replaced(self):
        video_path = r"C:\Users\Kleberson\Desktop\Programação\meus_projetos\Projeto_EduMind\video_teste.mp4"
        with open(video_path, "rb") as arquivo:
            arquivo_original = SimpleUploadedFile(
                "video_teste.mp4",
                arquivo.read(),
                content_type="video/mp4",
            )

        block = LessonBlock.objects.create(
            secao=self.section,
            tipo=LessonBlock.TIPO_VIDEO,
            titulo="Vídeo antigo",
            arquivo_video=arquivo_original,
            ordem=4,
            ativo=True,
        )

        with open(video_path, "rb") as arquivo:
            novo_video = SimpleUploadedFile(
                "video_teste_novo.mp4",
                arquivo.read(),
                content_type="video/mp4",
            )
        serializer = LessonBlockSerializer(
            instance=block,
            data={
                "tipo": LessonBlock.TIPO_VIDEO,
                "titulo": "Vídeo atualizado",
                "arquivo_video": novo_video,
                "ordem": 4,
                "ativo": True,
            },
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        block.refresh_from_db()
        self.assertTrue(block.arquivo_video)
        self.assertTrue(block.arquivo_video.name.endswith(".mp4"))


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

    def test_professor_can_update_section_for_lesson(self):
        section = LessonSection.objects.create(
            aula=self.lesson,
            titulo="Seção inicial",
            descricao="Descrição antiga.",
            ordem=1,
            ativo=True,
        )
        self.client.force_authenticate(user=self.professor)
        url = reverse(
            "classrooms-professor-section-detail",
            args=[self.classroom.id, self.lesson.id, section.id],
        )

        response = self.client.patch(
            url,
            {
                "titulo": "Seção atualizada",
                "descricao": "Descrição nova.",
                "ordem": 2,
                "ativo": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["titulo"], "Seção atualizada")
        self.assertEqual(response.data["descricao"], "Descrição nova.")
        self.assertFalse(response.data["ativo"])

    def test_professor_can_reorder_sections_for_lesson(self):
        section_1 = LessonSection.objects.create(
            aula=self.lesson,
            titulo="Seção 1",
            descricao="Primeira seção.",
            ordem=1,
            ativo=True,
        )
        section_2 = LessonSection.objects.create(
            aula=self.lesson,
            titulo="Seção 2",
            descricao="Segunda seção.",
            ordem=2,
            ativo=True,
        )

        self.client.force_authenticate(user=self.professor)
        url = reverse(
            "classrooms-professor-section-detail",
            args=[self.classroom.id, self.lesson.id, section_2.id],
        )

        response = self.client.patch(url, {"ordem": 1}, format="json")

        self.assertEqual(response.status_code, 200)
        section_1.refresh_from_db()
        section_2.refresh_from_db()
        self.assertEqual(section_1.ordem, 2)
        self.assertEqual(section_2.ordem, 1)


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

    def test_professor_can_update_block_for_section(self):
        block = LessonBlock.objects.create(
            secao=self.section,
            tipo=LessonBlock.TIPO_TEXTO,
            titulo="Texto original",
            conteudo="Conteúdo antigo.",
            ordem=1,
            ativo=True,
        )
        self.client.force_authenticate(user=self.professor)
        url = reverse(
            "classrooms-professor-block-detail",
            args=[self.classroom.id, self.lesson.id, self.section.id, block.id],
        )

        response = self.client.patch(
            url,
            {
                "titulo": "Texto atualizado",
                "conteudo": "Conteúdo novo.",
                "ordem": 2,
                "ativo": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["titulo"], "Texto atualizado")
        self.assertEqual(response.data["conteudo"], "Conteúdo novo.")
        self.assertFalse(response.data["ativo"])
