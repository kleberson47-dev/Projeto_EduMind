import tempfile
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.db.models import RestrictedError
from django.test import SimpleTestCase, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import (
    Activity,
    Classroom,
    ClassroomMaterial,
    Enrollment,
    Grade,
    Lesson,
    Module,
)
from .services_notas import (
    anotar_pesos_distribuidos,
    arredondar_nota,
    definir_modo_distribuicao,
    peso_para_nova_atividade,
)

User = get_user_model()
SENHA = "senha-de-teste-123"


# Hasher rápido apenas nos testes: o PBKDF2 padrão deixa cada setUp (4 usuários) muito lento.
@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class BaseAtividadesTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.prazo = timezone.localdate() + timedelta(days=30)

        self.professor = self.criar_usuario(
            "professor@atividades.com", "Professor", "professor")
        self.outro_professor = self.criar_usuario(
            "outro_professor@atividades.com", "Outro Professor", "professor")
        self.aluno = self.criar_usuario(
            "aluno@atividades.com", "Aluno", "aluno")
        self.aluno_externo = self.criar_usuario(
            "externo@atividades.com", "Aluno Externo", "aluno")

        self.turma = Classroom.objects.create(
            professor=self.professor,
            nome="Turma",
            codigo_acesso="ATV00001",
            ativo=True,
        )
        self.outra_turma = Classroom.objects.create(
            professor=self.outro_professor,
            nome="Outra turma",
            codigo_acesso="ATV00002",
            ativo=True,
        )
        Enrollment.objects.create(
            aluno=self.aluno, turma=self.turma, ativo=True)

        self.modulo = Module.objects.create(
            turma=self.turma,
            nome="Unidade 1",
            ordem=1,
            modo_distribuicao=Module.DISTRIBUICAO_LIVRE,
        )
        self.modulo_outra_turma = Module.objects.create(
            turma=self.outra_turma,
            nome="Unidade X",
            ordem=1,
            modo_distribuicao=Module.DISTRIBUICAO_LIVRE,
        )

    @staticmethod
    def criar_usuario(email, nome, role):
        return User.objects.create_user(
            email=email, password=SENHA, nome=nome, role=role)

    def login(self, usuario):
        self.client.force_authenticate(user=usuario)

    def url(self, nome, *args):
        return reverse(nome, args=args)

    def atividade(self, **extra):
        dados = {
            "turma": self.turma,
            "modulo": self.modulo,
            "titulo": "Prova 1",
            "tipo": Activity.TIPO_PROVA,
            "peso": Decimal("6.00"),
            "data_entrega": self.prazo,
        }
        dados.update(extra)
        return Activity.objects.create(**dados)

    def nota(self, atividade, valor="4.00", aluno=None):
        return Grade.objects.create(
            aluno=aluno or self.aluno,
            turma=atividade.turma,
            atividade=atividade,
            valor=Decimal(valor),
        )

    def payload(self, **extra):
        dados = {
            "modulo": self.modulo.id,
            "titulo": "Prova 1",
            "tipo": "prova",
            "peso": "6",
            "data_entrega": self.prazo.isoformat(),
        }
        dados.update(extra)
        return dados

    def criar_via_api(self, **extra):
        return self.client.post(
            self.url("classrooms-professor-activities", self.turma.id),
            self.payload(**extra),
            format="json",
        )


class ArredondarNotaTests(SimpleTestCase):
    def test_arredonda_para_duas_casas_e_sobe_quando_termina_em_99(self):
        casos = {
            "9.99": "10.00",
            "7.99": "8.00",
            "5.99": "6.00",
            "0.99": "1.00",
            "8.994": "9.00",
            "8.995": "9.00",
            "9.986": "10.00",
            "5.985": "6.00",
            "5.984": "5.98",
            "8.5": "8.50",
            "3.333": "3.33",
            "10": "10.00",
            "0": "0.00",
        }
        for entrada, esperado in casos.items():
            with self.subTest(entrada=entrada):
                self.assertEqual(str(arredondar_nota(entrada)), esperado)

    def test_aceita_decimal(self):
        self.assertEqual(str(arredondar_nota(Decimal("9.99"))), "10.00")


class ModuloApiTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.url_lista = self.url("classrooms-professor-modules", self.turma.id)

    def test_professor_cria_modulos_com_ordem_sequencial(self):
        self.login(self.professor)

        response = self.client.post(
            self.url_lista, {"nome": "  Unidade 2  "}, format="json")

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.data["nome"], "Unidade 2")
        self.assertEqual(response.data["ordem"], 2)
        self.assertIsNone(response.data["modo_distribuicao"])
        self.assertEqual(response.data["pesos_distribuidos"], "0.00")
        self.assertEqual(response.data["turma"], self.turma.id)

    def test_nome_em_branco_e_rejeitado(self):
        self.login(self.professor)

        response = self.client.post(
            self.url_lista, {"nome": "   "}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("nome", response.data)

    def test_lista_e_paginada_e_filtra_por_ativo(self):
        Module.objects.create(
            turma=self.turma, nome="Inativo", ordem=2, ativo=False)
        self.login(self.professor)

        todos = self.client.get(self.url_lista)
        ativos = self.client.get(self.url_lista, {"ativo": "true"})

        self.assertEqual(todos.status_code, 200)
        self.assertEqual(todos.data["count"], 2)
        self.assertIn("results", todos.data)
        self.assertEqual(ativos.data["count"], 1)

    def test_modulos_exigem_professor_dono_da_turma(self):
        self.login(self.aluno)
        self.assertEqual(self.client.get(self.url_lista).status_code, 403)
        self.assertEqual(self.client.post(
            self.url_lista, {"nome": "X"}, format="json").status_code, 403)

        self.login(self.outro_professor)
        self.assertEqual(self.client.get(self.url_lista).status_code, 404)

        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(self.url_lista).status_code, 401)

    def test_professor_renomeia_modulo(self):
        self.login(self.professor)
        url = self.url("classrooms-professor-module-detail",
                       self.turma.id, self.modulo.id)

        response = self.client.patch(url, {"nome": "Novo nome"}, format="json")

        self.assertEqual(response.status_code, 200, response.content)
        self.modulo.refresh_from_db()
        self.assertEqual(self.modulo.nome, "Novo nome")

    def test_campos_controlados_pelo_sistema_nao_sao_alterados(self):
        self.login(self.professor)
        url = self.url("classrooms-professor-module-detail",
                       self.turma.id, self.modulo.id)

        self.client.patch(
            url,
            {"ordem": 9, "modo_distribuicao": "media", "ativo": False},
            format="json",
        )

        self.modulo.refresh_from_db()
        self.assertEqual(self.modulo.ordem, 1)
        self.assertEqual(self.modulo.modo_distribuicao,
                         Module.DISTRIBUICAO_LIVRE)
        self.assertTrue(self.modulo.ativo)

    def test_nao_desativa_modulo_com_atividade_ativa(self):
        self.atividade()
        self.login(self.professor)
        url = self.url("classrooms-professor-module-detail",
                       self.turma.id, self.modulo.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.data)
        self.modulo.refresh_from_db()
        self.assertTrue(self.modulo.ativo)

    def test_desativa_modulo_sem_atividades_ativas(self):
        self.atividade(ativo=False)
        self.login(self.professor)
        url = self.url("classrooms-professor-module-detail",
                       self.turma.id, self.modulo.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.modulo.refresh_from_db()
        self.assertFalse(self.modulo.ativo)

    def test_modulo_de_outra_turma_nao_e_acessivel(self):
        self.login(self.professor)
        url = self.url("classrooms-professor-module-detail",
                       self.turma.id, self.modulo_outra_turma.id)

        self.assertEqual(self.client.get(url).status_code, 404)

    def test_soma_de_pesos_ignora_inativas_recuperacao_e_nao_pontuadas(self):
        self.atividade(titulo="Prova", peso=Decimal("6.00"))
        self.atividade(titulo="Inativa", tipo=Activity.TIPO_TESTE,
                       peso=Decimal("2.00"), ativo=False)
        self.atividade(titulo="Lista", tipo=Activity.TIPO_LISTA,
                       pontuada=False, peso=None)
        self.atividade(titulo="Rec", tipo=Activity.TIPO_RECUPERACAO,
                       peso=Decimal("10.00"), modo_recuperacao="unidade")
        self.login(self.professor)

        response = self.client.get(self.url_lista)

        self.assertEqual(response.data["results"][0]["pesos_distribuidos"], "6.00")

    def test_numero_de_consultas_nao_cresce_com_a_quantidade_de_modulos(self):
        self.login(self.professor)

        def consultas():
            with CaptureQueriesContext(connection) as contexto:
                response = self.client.get(self.url_lista)
            self.assertEqual(response.status_code, 200)
            return len(contexto)

        antes = consultas()
        for ordem in range(2, 7):
            modulo = Module.objects.create(
                turma=self.turma, nome=f"U{ordem}", ordem=ordem)
            self.atividade(modulo=modulo, titulo=f"A{ordem}")
        depois = consultas()

        self.assertEqual(antes, depois)


class CriterioDistribuicaoTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.modulo_novo = Module.objects.create(
            turma=self.turma, nome="Unidade 2", ordem=2)
        self.url_criterio = self.url(
            "classrooms-professor-module-distribution",
            self.turma.id,
            self.modulo_novo.id,
        )

    def definir(self, modo):
        return self.client.post(self.url_criterio, {"modo": modo}, format="json")

    def test_define_criterio_uma_unica_vez(self):
        self.login(self.professor)

        primeira = self.definir("livre")
        segunda = self.definir("media")

        self.assertEqual(primeira.status_code, 200, primeira.content)
        self.assertEqual(primeira.data["modo_distribuicao"], "livre")
        self.assertEqual(segunda.status_code, 400)
        self.modulo_novo.refresh_from_db()
        self.assertEqual(self.modulo_novo.modo_distribuicao, "livre")

    def test_criterio_invalido_e_rejeitado(self):
        self.login(self.professor)

        response = self.definir("aleatorio")

        self.assertEqual(response.status_code, 400)
        self.assertIn("modo", response.data)

    def test_somente_o_professor_dono_define_criterio(self):
        self.login(self.aluno)
        self.assertEqual(self.definir("livre").status_code, 403)

        self.login(self.outro_professor)
        self.assertEqual(self.definir("livre").status_code, 404)

    def test_atividade_pontuada_exige_criterio_definido(self):
        self.login(self.professor)

        response = self.criar_via_api(modulo=self.modulo_novo.id)

        self.assertEqual(response.status_code, 400)

    def test_atividade_sem_pontuacao_nao_exige_criterio(self):
        self.login(self.professor)

        response = self.client.post(
            self.url("classrooms-professor-activities", self.turma.id),
            {
                "modulo": self.modulo_novo.id,
                "titulo": "Lista de leitura",
                "tipo": "lista",
                "pontuada": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertIsNone(response.data["peso"])

    def test_criterio_media_fixa_o_peso_em_10(self):
        self.login(self.professor)
        self.definir("media")

        primeira = self.criar_via_api(modulo=self.modulo_novo.id, peso=None)
        segunda = self.criar_via_api(
            modulo=self.modulo_novo.id, titulo="Prova 2", peso=None)

        self.assertEqual(primeira.status_code, 201, primeira.content)
        self.assertEqual(primeira.data["peso"], "10.00")
        self.assertEqual(segunda.status_code, 201, segunda.content)
        self.assertEqual(segunda.data["peso"], "10.00")

    def test_criterio_media_rejeita_peso_diferente_de_10(self):
        self.login(self.professor)
        self.definir("media")

        response = self.criar_via_api(modulo=self.modulo_novo.id, peso="5")

        self.assertEqual(response.status_code, 400)

    def test_criterio_livre_limita_a_soma_dos_pesos_em_10(self):
        self.login(self.professor)

        prova = self.criar_via_api(peso="6")
        teste = self.criar_via_api(titulo="Teste", tipo="teste", peso="3")
        excedente = self.criar_via_api(
            titulo="Trabalho", tipo="trabalho", peso="2")
        exato = self.criar_via_api(
            titulo="Trabalho", tipo="trabalho", peso="1")

        self.assertEqual(prova.status_code, 201, prova.content)
        self.assertEqual(teste.status_code, 201, teste.content)
        self.assertEqual(excedente.status_code, 400)
        self.assertEqual(exato.status_code, 201, exato.content)

    def test_criterio_livre_exige_peso_valido(self):
        self.login(self.professor)

        sem_peso = self.criar_via_api(peso=None)
        zero = self.criar_via_api(peso="0")
        acima = self.criar_via_api(peso="10.5")

        self.assertEqual(sem_peso.status_code, 400)
        self.assertEqual(zero.status_code, 400)
        self.assertEqual(acima.status_code, 400)

    def test_recuperacao_vale_10_e_nao_consome_pontos_do_modulo(self):
        self.login(self.professor)
        self.criar_via_api(peso="10")

        response = self.criar_via_api(
            titulo="Recuperação",
            tipo="recuperacao",
            peso=None,
            modo_recuperacao="prova",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.data["peso"], "10.00")

    def test_atividade_sem_pontuacao_nao_aceita_peso(self):
        self.login(self.professor)

        response = self.criar_via_api(
            titulo="Lista", tipo="lista", pontuada=False, peso="1")

        self.assertEqual(response.status_code, 400)

    def test_servico_definir_modo_rejeita_modulo_inativo(self):
        self.modulo_novo.ativo = False
        self.modulo_novo.save()

        with self.assertRaises(ValidationError):
            definir_modo_distribuicao(self.modulo_novo, "livre")

    def test_servico_calcula_peso_conforme_o_criterio(self):
        self.assertEqual(
            peso_para_nova_atividade(
                self.modulo, Activity.TIPO_PROVA, True, "4"),
            Decimal("4.00"),
        )
        modulo_media = Module.objects.create(
            turma=self.turma,
            nome="Média",
            ordem=3,
            modo_distribuicao=Module.DISTRIBUICAO_MEDIA,
        )
        self.assertEqual(
            peso_para_nova_atividade(
                modulo_media, Activity.TIPO_PROVA, True),
            Decimal("10.00"),
        )


class AtividadeCriacaoTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.login(self.professor)

    def test_cria_atividade_nao_publicada_com_dados_completos(self):
        response = self.criar_via_api(descricao="Capítulos 1 a 3")

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.data["turma"], self.turma.id)
        self.assertEqual(response.data["modulo"], self.modulo.id)
        self.assertEqual(response.data["peso"], "6.00")
        self.assertTrue(response.data["pontuada"])
        self.assertFalse(response.data["publicado"])

    def test_publicado_nao_pode_ser_definido_na_criacao(self):
        response = self.criar_via_api(publicado=True)

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data["publicado"])

    def test_tipo_e_obrigatorio(self):
        dados = self.payload()
        dados.pop("tipo")

        response = self.client.post(
            self.url("classrooms-professor-activities", self.turma.id),
            dados,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("tipo", response.data)

    def test_tipos_removidos_sao_rejeitados(self):
        for tipo in ("atividade", "material"):
            with self.subTest(tipo=tipo):
                response = self.criar_via_api(tipo=tipo)
                self.assertEqual(response.status_code, 400)
                self.assertIn("tipo", response.data)

    def test_todos_os_tipos_validos_sao_aceitos(self):
        for tipo, extra in (
            ("trabalho", {}),
            ("prova", {}),
            ("teste", {}),
            ("lista", {}),
            ("recuperacao", {"modo_recuperacao": "unidade", "peso": None}),
        ):
            with self.subTest(tipo=tipo):
                self.modulo.atividades.all().delete()
                response = self.criar_via_api(
                    titulo=tipo.title(), tipo=tipo, **extra)
                self.assertEqual(response.status_code, 201, response.content)

    def test_titulo_em_branco_e_rejeitado(self):
        response = self.criar_via_api(titulo="   ")

        self.assertEqual(response.status_code, 400)
        self.assertIn("titulo", response.data)

    def test_modulo_de_outra_turma_e_rejeitado(self):
        response = self.criar_via_api(modulo=self.modulo_outra_turma.id)

        self.assertEqual(response.status_code, 400)
        self.assertIn("modulo", response.data)

    def test_modulo_inativo_e_rejeitado(self):
        self.modulo.ativo = False
        self.modulo.save()

        response = self.criar_via_api()

        self.assertEqual(response.status_code, 400)
        self.assertIn("modulo", response.data)

    def test_modulo_e_obrigatorio(self):
        dados = self.payload()
        dados.pop("modulo")

        response = self.client.post(
            self.url("classrooms-professor-activities", self.turma.id),
            dados,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("modulo", response.data)

    def test_atividade_pontuada_exige_data_de_entrega(self):
        dados = self.payload()
        dados.pop("data_entrega")

        response = self.client.post(
            self.url("classrooms-professor-activities", self.turma.id),
            dados,
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_prova_nao_pode_ser_sem_pontuacao(self):
        response = self.criar_via_api(pontuada=False, peso=None)

        self.assertEqual(response.status_code, 400)

    def test_data_de_inicio_nao_pode_ser_apos_a_entrega(self):
        inicio = (self.prazo + timedelta(days=1)).isoformat()

        response = self.criar_via_api(data_inicio=inicio)

        self.assertEqual(response.status_code, 400)

    def test_revisoes_so_valem_para_trabalho(self):
        prova = self.criar_via_api(max_revisoes=2)
        trabalho = self.criar_via_api(
            titulo="Trabalho", tipo="trabalho", peso="3", max_revisoes=2)

        self.assertEqual(prova.status_code, 400)
        self.assertEqual(trabalho.status_code, 201, trabalho.content)
        self.assertEqual(trabalho.data["max_revisoes"], 2)

    def test_sorteio_so_vale_para_tipos_com_questoes(self):
        trabalho = self.criar_via_api(
            tipo="trabalho", peso="3", quantidade_sorteio=5)
        prova = self.criar_via_api(quantidade_sorteio=5)

        self.assertEqual(trabalho.status_code, 400)
        self.assertEqual(prova.status_code, 201, prova.content)

    def test_recuperacao_exige_modo_e_modo_so_vale_para_recuperacao(self):
        sem_modo = self.criar_via_api(
            titulo="Rec", tipo="recuperacao", peso=None)
        modo_em_prova = self.criar_via_api(modo_recuperacao="unidade")

        self.assertEqual(sem_modo.status_code, 400)
        self.assertEqual(modo_em_prova.status_code, 400)

    def test_somente_professor_dono_cria_atividade(self):
        self.login(self.aluno)
        self.assertEqual(self.criar_via_api().status_code, 403)

        self.login(self.outro_professor)
        self.assertEqual(self.criar_via_api().status_code, 404)

        self.client.force_authenticate(user=None)
        self.assertEqual(self.criar_via_api().status_code, 401)

    def test_lista_com_filtros_e_paginacao(self):
        outro_modulo = Module.objects.create(
            turma=self.turma, nome="Unidade 2", ordem=2,
            modo_distribuicao=Module.DISTRIBUICAO_LIVRE)
        self.atividade(titulo="Prova", tipo=Activity.TIPO_PROVA)
        self.atividade(titulo="Teste", tipo=Activity.TIPO_TESTE,
                       peso=Decimal("2.00"), publicado=True)
        self.atividade(titulo="Trab", tipo=Activity.TIPO_TRABALHO,
                       modulo=outro_modulo, peso=Decimal("5.00"),
                       data_entrega=self.prazo + timedelta(days=10))
        url = self.url("classrooms-professor-activities", self.turma.id)

        total = self.client.get(url)
        por_tipo = self.client.get(url, {"tipo": "prova"})
        por_modulo = self.client.get(url, {"modulo": outro_modulo.id})
        publicadas = self.client.get(url, {"publicado": "true"})
        ate = self.client.get(
            url, {"data_entrega_ate": self.prazo.isoformat()})
        de = self.client.get(
            url,
            {"data_entrega_de": (self.prazo + timedelta(days=5)).isoformat()},
        )

        self.assertEqual(total.data["count"], 3)
        self.assertEqual(por_tipo.data["count"], 1)
        self.assertEqual(por_modulo.data["count"], 1)
        self.assertEqual(publicadas.data["count"], 1)
        self.assertEqual(ate.data["count"], 2)
        self.assertEqual(de.data["count"], 1)

    def test_lista_nao_mostra_atividades_de_outra_turma(self):
        Activity.objects.create(
            turma=self.outra_turma,
            modulo=self.modulo_outra_turma,
            titulo="Alheia",
            tipo=Activity.TIPO_PROVA,
            peso=Decimal("5.00"),
            data_entrega=self.prazo,
        )

        response = self.client.get(
            self.url("classrooms-professor-activities", self.turma.id))

        self.assertEqual(response.data["count"], 0)


class AtividadeEdicaoTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.prova = self.atividade(titulo="Prova", peso=Decimal("6.00"))
        self.teste = self.atividade(
            titulo="Teste", tipo=Activity.TIPO_TESTE, peso=Decimal("3.00"))
        self.login(self.professor)

    def editar(self, atividade, dados, usuario=None):
        if usuario is not None:
            self.login(usuario)
        return self.client.patch(
            self.url("classrooms-professor-activity-detail",
                     self.turma.id, atividade.id),
            dados,
            format="json",
        )

    def test_edita_titulo_descricao_e_prazo(self):
        novo_prazo = (self.prazo + timedelta(days=7)).isoformat()

        response = self.editar(self.prova, {
            "titulo": "  Prova final  ",
            "descricao": "Conteúdo revisado",
            "data_entrega": novo_prazo,
        })

        self.assertEqual(response.status_code, 200, response.content)
        self.prova.refresh_from_db()
        self.assertEqual(self.prova.titulo, "Prova final")
        self.assertEqual(self.prova.descricao, "Conteúdo revisado")
        self.assertEqual(self.prova.data_entrega.isoformat(), novo_prazo)

    def test_titulo_em_branco_e_rejeitado_na_edicao(self):
        response = self.editar(self.prova, {"titulo": " "})

        self.assertEqual(response.status_code, 400)

    def test_edita_peso_dentro_do_limite_do_modulo(self):
        response = self.editar(self.prova, {"peso": "7"})

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.data["peso"], "7.00")

    def test_rejeita_peso_que_excede_os_pontos_do_modulo(self):
        response = self.editar(self.prova, {"peso": "8"})

        self.assertEqual(response.status_code, 400)
        self.prova.refresh_from_db()
        self.assertEqual(self.prova.peso, Decimal("6.00"))

    def test_reduzir_peso_libera_pontos_para_novas_atividades(self):
        self.editar(self.prova, {"peso": "2"})

        response = self.criar_via_api(
            titulo="Trabalho", tipo="trabalho", peso="5")

        self.assertEqual(response.status_code, 201, response.content)

    def test_nao_altera_o_tipo(self):
        response = self.editar(self.prova, {"tipo": "teste"})

        self.assertEqual(response.status_code, 400)
        self.prova.refresh_from_db()
        self.assertEqual(self.prova.tipo, Activity.TIPO_PROVA)

    def test_nao_altera_o_modulo(self):
        outro_modulo = Module.objects.create(
            turma=self.turma, nome="Unidade 2", ordem=2)

        response = self.editar(self.prova, {"modulo": outro_modulo.id})

        self.assertEqual(response.status_code, 400)
        self.assertIn("modulo", response.data)
        self.prova.refresh_from_db()
        self.assertEqual(self.prova.modulo_id, self.modulo.id)

    def test_publicado_nao_e_editavel_por_patch(self):
        response = self.editar(self.prova, {"publicado": True})

        self.assertEqual(response.status_code, 200)
        self.prova.refresh_from_db()
        self.assertFalse(self.prova.publicado)

    def test_rejeita_data_de_inicio_posterior_a_entrega(self):
        inicio = (self.prazo + timedelta(days=1)).isoformat()

        response = self.editar(self.prova, {"data_inicio": inicio})

        self.assertEqual(response.status_code, 400)

    def test_com_notas_o_peso_fica_bloqueado(self):
        self.nota(self.prova)

        response = self.editar(self.prova, {"peso": "5"})

        self.assertEqual(response.status_code, 400)
        self.prova.refresh_from_db()
        self.assertEqual(self.prova.peso, Decimal("6.00"))

    def test_com_notas_ainda_permite_titulo_e_o_mesmo_peso(self):
        self.nota(self.prova)

        response = self.editar(
            self.prova, {"titulo": "Prova 1 (revisada)", "peso": "6"})

        self.assertEqual(response.status_code, 200, response.content)
        self.prova.refresh_from_db()
        self.assertEqual(self.prova.titulo, "Prova 1 (revisada)")

    def test_com_notas_a_pontuacao_fica_bloqueada(self):
        lista = self.atividade(
            titulo="Lista", tipo=Activity.TIPO_LISTA, peso=Decimal("1.00"))
        self.nota(lista, valor="1.00")

        response = self.editar(lista, {"pontuada": False})

        self.assertEqual(response.status_code, 400)
        lista.refresh_from_db()
        self.assertTrue(lista.pontuada)

    def test_lista_sem_notas_pode_deixar_de_ser_pontuada(self):
        lista = self.atividade(
            titulo="Lista", tipo=Activity.TIPO_LISTA, peso=Decimal("1.00"))

        response = self.editar(lista, {"pontuada": False})

        self.assertEqual(response.status_code, 200, response.content)
        lista.refresh_from_db()
        self.assertFalse(lista.pontuada)
        self.assertIsNone(lista.peso)

    def test_desativar_por_patch_libera_pontos(self):
        response = self.editar(self.teste, {"ativo": False})

        self.assertEqual(response.status_code, 200)
        criada = self.criar_via_api(
            titulo="Trabalho", tipo="trabalho", peso="4")
        self.assertEqual(criada.status_code, 201, criada.content)

    def test_reativar_respeita_o_limite_de_pontos(self):
        self.editar(self.teste, {"ativo": False})
        self.criar_via_api(titulo="Trabalho", tipo="trabalho", peso="4")

        response = self.editar(self.teste, {"ativo": True})

        self.assertEqual(response.status_code, 400)
        self.teste.refresh_from_db()
        self.assertFalse(self.teste.ativo)

    def test_edicao_exige_professor_dono(self):
        aluno = self.editar(self.prova, {"titulo": "X"}, usuario=self.aluno)
        outro = self.editar(
            self.prova, {"titulo": "X"}, usuario=self.outro_professor)
        self.client.force_authenticate(user=None)
        anonimo = self.editar(self.prova, {"titulo": "X"})

        self.assertEqual(aluno.status_code, 403)
        self.assertEqual(outro.status_code, 404)
        self.assertEqual(anonimo.status_code, 401)
        self.prova.refresh_from_db()
        self.assertEqual(self.prova.titulo, "Prova")

    def test_detalhe_retorna_a_atividade(self):
        response = self.client.get(
            self.url("classrooms-professor-activity-detail",
                     self.turma.id, self.prova.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.prova.id)


class AtividadeExclusaoTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.prova = self.atividade(titulo="Prova", peso=Decimal("6.00"))
        self.teste = self.atividade(
            titulo="Teste", tipo=Activity.TIPO_TESTE, peso=Decimal("3.00"))
        self.login(self.professor)

    def excluir(self, atividade, usuario=None):
        if usuario is not None:
            self.login(usuario)
        return self.client.delete(
            self.url("classrooms-professor-activity-detail",
                     self.turma.id, atividade.id))

    def test_exclui_atividade_sem_historico(self):
        response = self.excluir(self.prova)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Activity.objects.filter(pk=self.prova.pk).exists())

    def test_exclusao_libera_os_pontos_do_modulo(self):
        self.excluir(self.prova)

        response = self.criar_via_api(
            titulo="Trabalho", tipo="trabalho", peso="7")

        self.assertEqual(response.status_code, 201, response.content)

    def test_com_notas_apenas_desativa_e_preserva_a_nota(self):
        nota = self.nota(self.prova)

        response = self.excluir(self.prova)

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.data["resultado"], "desativada")
        self.prova.refresh_from_db()
        self.assertFalse(self.prova.ativo)
        self.assertTrue(Grade.objects.filter(pk=nota.pk).exists())

    def test_atividade_desativada_nao_consome_pontos(self):
        self.nota(self.prova)
        self.excluir(self.prova)

        response = self.criar_via_api(
            titulo="Trabalho", tipo="trabalho", peso="7")

        self.assertEqual(response.status_code, 201, response.content)

    def test_exclusao_exige_professor_dono(self):
        aluno = self.excluir(self.prova, usuario=self.aluno)
        outro = self.excluir(self.prova, usuario=self.outro_professor)
        self.client.force_authenticate(user=None)
        anonimo = self.excluir(self.prova)

        self.assertEqual(aluno.status_code, 403)
        self.assertEqual(outro.status_code, 404)
        self.assertEqual(anonimo.status_code, 401)
        self.assertTrue(Activity.objects.filter(pk=self.prova.pk).exists())

    def test_excluir_atividade_inexistente_retorna_404(self):
        self.excluir(self.prova)

        self.assertEqual(self.excluir(self.prova).status_code, 404)


class AtividadeVisibilidadeTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.url_aluno = self.url(
            "classrooms-student-activities", self.turma.id)

    def titulos(self, usuario):
        self.login(usuario)
        response = self.client.get(self.url_aluno)
        self.assertEqual(response.status_code, 200)
        return [item["titulo"] for item in response.data]

    def test_rascunho_nao_aparece_para_o_aluno(self):
        self.atividade(titulo="Rascunho")

        self.assertEqual(self.titulos(self.aluno), [])

    def test_publicar_torna_a_atividade_visivel(self):
        prova = self.atividade(titulo="Prova")
        self.login(self.professor)

        response = self.client.post(self.url(
            "classrooms-professor-activity-publish", self.turma.id, prova.id))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.data["publicado"])
        self.assertEqual(self.titulos(self.aluno), ["Prova"])

    def test_publicar_duas_vezes_e_rejeitado(self):
        prova = self.atividade(titulo="Prova", publicado=True)
        self.login(self.professor)

        response = self.client.post(self.url(
            "classrooms-professor-activity-publish", self.turma.id, prova.id))

        self.assertEqual(response.status_code, 400)

    def test_atividade_inativa_nao_pode_ser_publicada(self):
        prova = self.atividade(titulo="Prova", ativo=False)
        self.login(self.professor)

        response = self.client.post(self.url(
            "classrooms-professor-activity-publish", self.turma.id, prova.id))

        self.assertEqual(response.status_code, 400)

    def test_publicacao_exige_professor_dono(self):
        prova = self.atividade(titulo="Prova")
        url = self.url("classrooms-professor-activity-publish",
                       self.turma.id, prova.id)

        self.login(self.aluno)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.login(self.outro_professor)
        self.assertEqual(self.client.post(url).status_code, 404)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.post(url).status_code, 401)

    def test_data_de_inicio_futura_oculta_ate_o_dia(self):
        hoje = timezone.localdate()
        self.atividade(titulo="Hoje", publicado=True, data_inicio=hoje)
        self.atividade(titulo="Amanhã", publicado=True,
                       data_inicio=hoje + timedelta(days=1))
        self.atividade(titulo="Sem início", publicado=True)

        self.assertCountEqual(
            self.titulos(self.aluno), ["Hoje", "Sem início"])

    def test_atividade_inativa_nao_aparece(self):
        self.atividade(titulo="Inativa", publicado=True, ativo=False)

        self.assertEqual(self.titulos(self.aluno), [])

    def test_aluno_sem_matricula_ativa_nao_ve_atividades(self):
        self.atividade(titulo="Prova", publicado=True)

        self.assertEqual(self.titulos(self.aluno_externo), [])

        Enrollment.objects.filter(aluno=self.aluno).update(ativo=False)
        self.assertEqual(self.titulos(self.aluno), [])

    def test_nao_mostra_atividades_de_outra_turma(self):
        Activity.objects.create(
            turma=self.outra_turma,
            modulo=self.modulo_outra_turma,
            titulo="Alheia",
            tipo=Activity.TIPO_PROVA,
            peso=Decimal("5.00"),
            data_entrega=self.prazo,
            publicado=True,
        )

        self.assertEqual(self.titulos(self.aluno), [])


class NotaTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.prova = self.atividade(titulo="Prova", peso=Decimal("6.00"))
        self.url_notas = self.url(
            "classrooms-professor-grades", self.turma.id)
        self.login(self.professor)

    def lancar(self, valor="4", atividade=None, aluno=None):
        return self.client.post(
            self.url_notas,
            {
                "aluno": (aluno or self.aluno).id,
                "atividade": (atividade or self.prova).id,
                "valor": valor,
            },
            format="json",
        )

    def test_lanca_nota_dentro_do_peso(self):
        response = self.lancar("5.5")

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.data["valor"], "5.50")
        self.assertEqual(
            Grade.objects.get(pk=response.data["id"]).origem,
            Grade.ORIGEM_MANUAL,
        )

    def test_aceita_nota_igual_ao_peso(self):
        self.assertEqual(self.lancar("6").status_code, 201)

    def test_rejeita_nota_acima_do_peso(self):
        response = self.lancar("6.01")

        self.assertEqual(response.status_code, 400)
        self.assertIn("valor", response.data)

    def test_rejeita_nota_negativa_e_acima_de_10(self):
        self.assertEqual(self.lancar("-1").status_code, 400)
        self.assertEqual(self.lancar("11").status_code, 400)

    def test_rejeita_nota_em_atividade_sem_pontuacao(self):
        lista = self.atividade(
            titulo="Lista", tipo=Activity.TIPO_LISTA,
            pontuada=False, peso=None)

        self.assertEqual(self.lancar("1", atividade=lista).status_code, 400)

    def test_rejeita_nota_em_atividade_inativa(self):
        self.prova.ativo = False
        self.prova.save()

        self.assertEqual(self.lancar().status_code, 400)

    def test_rejeita_atividade_de_outra_turma(self):
        alheia = Activity.objects.create(
            turma=self.outra_turma,
            modulo=self.modulo_outra_turma,
            titulo="Alheia",
            tipo=Activity.TIPO_PROVA,
            peso=Decimal("5.00"),
            data_entrega=self.prazo,
        )

        self.assertEqual(self.lancar(atividade=alheia).status_code, 400)

    def test_rejeita_aluno_nao_matriculado(self):
        response = self.lancar(aluno=self.aluno_externo)

        self.assertEqual(response.status_code, 400)

    def test_rejeita_nota_duplicada(self):
        self.lancar()

        self.assertEqual(self.lancar("3").status_code, 400)
        self.assertEqual(Grade.objects.count(), 1)

    def test_aluno_lista_apenas_as_proprias_notas(self):
        self.nota(self.prova, "4.00")
        outro = self.criar_usuario("outro@atividades.com", "Outro", "aluno")
        Enrollment.objects.create(aluno=outro, turma=self.turma, ativo=True)
        self.nota(self.prova, "2.00", aluno=outro)

        self.login(self.aluno)
        response = self.client.get(
            self.url("classrooms-student-grades", self.turma.id))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([n["valor"] for n in response.data], ["4.00"])


class MaterialTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        pasta = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(pasta.cleanup)
        self.storage = FileSystemStorage(location=pasta.name)
        campo = ClassroomMaterial._meta.get_field("arquivo")
        patcher = mock.patch.object(campo, "storage", self.storage)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.url_lista = self.url("classrooms-professor-materials", self.turma.id)
        self.url_aluno = self.url("classrooms-student-materials", self.turma.id)

    def enviar(self, nome="apostila.pdf", conteudo=b"%PDF-1.4 conteudo", **extra):
        dados = {
            "titulo": "Apostila",
            "arquivo": SimpleUploadedFile(
                nome, conteudo, content_type="application/pdf"),
        }
        dados.update(extra)
        return self.client.post(self.url_lista, dados, format="multipart")

    def criar_material(self, **extra):
        self.login(self.professor)
        response = self.enviar(**extra)
        self.assertEqual(response.status_code, 201, response.content)
        return ClassroomMaterial.objects.get(pk=response.data["id"])

    def url_detalhe(self, material):
        return self.url("classrooms-professor-material-detail",
                        self.turma.id, material.id)

    def url_download(self, material):
        return self.url("classrooms-material-download",
                        self.turma.id, material.id)

    def test_cria_material_ativo_sem_expor_o_caminho_do_arquivo(self):
        self.login(self.professor)

        response = self.enviar(modulo=self.modulo.id)

        self.assertEqual(response.status_code, 201, response.content)
        self.assertTrue(response.data["ativo"])
        self.assertNotIn("arquivo", response.data)
        self.assertTrue(response.data["arquivo_nome"].startswith("apostila"))
        material = ClassroomMaterial.objects.get(pk=response.data["id"])
        self.assertTrue(material.ativo)
        self.assertEqual(material.modulo_id, self.modulo.id)
        self.assertTrue(self.storage.exists(material.arquivo.name))
        self.assertIn(f"turma_{self.turma.id}", material.arquivo.name)

    def test_extensao_em_maiusculas_e_aceita(self):
        self.login(self.professor)

        self.assertEqual(self.enviar(nome="APOSTILA.PDF").status_code, 201)

    def test_rejeita_extensao_invalida_e_dupla_extensao(self):
        self.login(self.professor)

        for nome in ("virus.exe", "script.pdf.exe", "sem_extensao"):
            with self.subTest(nome=nome):
                response = self.enviar(nome=nome)
                self.assertEqual(response.status_code, 400)
                self.assertIn("arquivo", response.data)

    def test_rejeita_arquivo_acima_do_limite(self):
        self.login(self.professor)

        with mock.patch(
            "turmas.serializers.material_serializers.MAX_SIZE_MATERIAL_MB", 0
        ):
            response = self.enviar()

        self.assertEqual(response.status_code, 400)

    def test_arquivo_e_titulo_sao_obrigatorios(self):
        self.login(self.professor)

        sem_arquivo = self.client.post(
            self.url_lista, {"titulo": "Sem arquivo"}, format="multipart")
        titulo_em_branco = self.enviar(titulo="  ")

        self.assertEqual(sem_arquivo.status_code, 400)
        self.assertEqual(titulo_em_branco.status_code, 400)

    def test_rejeita_modulo_de_outra_turma(self):
        self.login(self.professor)

        response = self.enviar(modulo=self.modulo_outra_turma.id)

        self.assertEqual(response.status_code, 400)
        self.assertIn("modulo", response.data)

    def test_somente_professor_dono_cria_material(self):
        self.login(self.aluno)
        self.assertEqual(self.enviar().status_code, 403)
        self.login(self.outro_professor)
        self.assertEqual(self.enviar().status_code, 404)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.enviar().status_code, 401)

    def test_professor_lista_e_filtra_por_modulo(self):
        self.criar_material(modulo=self.modulo.id)
        self.criar_material(titulo="Sem módulo")

        todos = self.client.get(self.url_lista)
        filtrado = self.client.get(self.url_lista, {"modulo": self.modulo.id})

        self.assertEqual(todos.data["count"], 2)
        self.assertEqual(filtrado.data["count"], 1)

    def test_aluno_lista_apenas_materiais_ativos_da_sua_turma(self):
        ativo = self.criar_material(titulo="Ativo")
        inativo = self.criar_material(titulo="Inativo")
        ClassroomMaterial.objects.filter(pk=inativo.pk).update(ativo=False)
        self.assertTrue(ativo.ativo)

        self.login(self.aluno)
        response = self.client.get(self.url_aluno)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [m["titulo"] for m in response.data["results"]], ["Ativo"])

    def test_aluno_sem_matricula_ativa_nao_lista_materiais(self):
        self.criar_material()

        self.login(self.aluno_externo)
        self.assertEqual(self.client.get(self.url_aluno).data["count"], 0)

        Enrollment.objects.filter(aluno=self.aluno).update(ativo=False)
        self.login(self.aluno)
        self.assertEqual(self.client.get(self.url_aluno).data["count"], 0)

    def test_aluno_matriculado_baixa_o_arquivo_como_anexo(self):
        material = self.criar_material()
        self.login(self.aluno)

        response = self.client.get(self.url_download(material))
        conteudo = b"".join(response.streaming_content)
        response.close()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(conteudo, b"%PDF-1.4 conteudo")
        self.assertTrue(response["Content-Disposition"].startswith("attachment"))
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")

    def test_professor_dono_baixa_inclusive_material_inativo(self):
        material = self.criar_material()
        ClassroomMaterial.objects.filter(pk=material.pk).update(ativo=False)

        response = self.client.get(self.url_download(material))
        response.close()

        self.assertEqual(response.status_code, 200)

    def test_download_bloqueado_para_quem_nao_tem_acesso(self):
        material = self.criar_material()
        url = self.url_download(material)

        self.login(self.aluno_externo)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.login(self.outro_professor)
        self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get(url).status_code, 401)

    def test_aluno_nao_baixa_material_inativo(self):
        material = self.criar_material()
        ClassroomMaterial.objects.filter(pk=material.pk).update(ativo=False)

        self.login(self.aluno)

        self.assertEqual(
            self.client.get(self.url_download(material)).status_code, 404)

    def test_download_de_arquivo_ausente_retorna_404(self):
        material = self.criar_material()
        self.storage.delete(material.arquivo.name)

        self.assertEqual(
            self.client.get(self.url_download(material)).status_code, 404)

    def test_download_nao_aceita_material_de_outra_turma(self):
        material = self.criar_material()
        url = self.url("classrooms-material-download",
                       self.outra_turma.id, material.id)

        self.login(self.outro_professor)

        self.assertEqual(self.client.get(url).status_code, 404)

    def test_editar_titulo_mantem_o_arquivo(self):
        material = self.criar_material()
        arquivo = material.arquivo.name

        response = self.client.patch(
            self.url_detalhe(material), {"titulo": "Novo título"},
            format="json")

        self.assertEqual(response.status_code, 200, response.content)
        material.refresh_from_db()
        self.assertEqual(material.titulo, "Novo título")
        self.assertEqual(material.arquivo.name, arquivo)
        self.assertTrue(self.storage.exists(arquivo))

    def test_substituir_arquivo_remove_o_antigo(self):
        material = self.criar_material()
        antigo = material.arquivo.name

        response = self.client.patch(
            self.url_detalhe(material),
            {"arquivo": SimpleUploadedFile("novo.pdf", b"%PDF novo")},
            format="multipart",
        )

        self.assertEqual(response.status_code, 200, response.content)
        material.refresh_from_db()
        self.assertNotEqual(material.arquivo.name, antigo)
        self.assertFalse(self.storage.exists(antigo))
        self.assertTrue(self.storage.exists(material.arquivo.name))

    def test_excluir_remove_registro_e_arquivo(self):
        material = self.criar_material()
        arquivo = material.arquivo.name

        response = self.client.delete(self.url_detalhe(material))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(
            ClassroomMaterial.objects.filter(pk=material.pk).exists())
        self.assertFalse(self.storage.exists(arquivo))

    def test_outro_professor_nao_edita_nem_exclui(self):
        material = self.criar_material()

        self.login(self.outro_professor)
        editar = self.client.patch(
            self.url_detalhe(material), {"titulo": "X"}, format="json")
        excluir = self.client.delete(self.url_detalhe(material))

        self.assertEqual(editar.status_code, 404)
        self.assertEqual(excluir.status_code, 404)
        self.assertTrue(
            ClassroomMaterial.objects.filter(pk=material.pk).exists())


class AulaModuloTests(BaseAtividadesTestCase):
    def setUp(self):
        super().setUp()
        self.login(self.professor)

    def criar_aula(self, **extra):
        return self.client.post(
            self.url("classrooms-professor-lessons", self.turma.id),
            {"titulo": "Aula 1", "ordem": 1, **extra},
            format="json",
        )

    def test_aula_pode_ser_criada_com_ou_sem_modulo(self):
        com_modulo = self.criar_aula(modulo=self.modulo.id)
        sem_modulo = self.criar_aula(titulo="Aula 2", ordem=2)

        self.assertEqual(com_modulo.status_code, 201, com_modulo.content)
        self.assertEqual(com_modulo.data["modulo"], self.modulo.id)
        self.assertEqual(sem_modulo.status_code, 201, sem_modulo.content)
        self.assertIsNone(sem_modulo.data["modulo"])

    def test_aula_rejeita_modulo_de_outra_turma(self):
        response = self.criar_aula(modulo=self.modulo_outra_turma.id)

        self.assertEqual(response.status_code, 400)
        self.assertIn("modulo", response.data)

    def test_aula_muda_e_remove_o_modulo(self):
        aula = Lesson.objects.create(
            turma=self.turma, titulo="Aula", ordem=1, modulo=self.modulo)
        url = self.url("classrooms-professor-lesson-detail",
                       self.turma.id, aula.id)

        remover = self.client.patch(url, {"modulo": None}, format="json")

        self.assertEqual(remover.status_code, 200, remover.content)
        aula.refresh_from_db()
        self.assertIsNone(aula.modulo_id)

    def test_modulo_excluido_nao_apaga_a_aula(self):
        modulo = Module.objects.create(
            turma=self.turma, nome="Vazio", ordem=2)
        aula = Lesson.objects.create(
            turma=self.turma, titulo="Aula", ordem=1, modulo=modulo)

        modulo.delete()

        aula.refresh_from_db()
        self.assertIsNone(aula.modulo_id)


class IntegridadeTests(BaseAtividadesTestCase):
    def test_modulo_com_atividades_nao_pode_ser_apagado_isoladamente(self):
        self.atividade()

        with self.assertRaises(RestrictedError):
            self.modulo.delete()

    def test_atividade_com_notas_nao_pode_ser_apagada_isoladamente(self):
        prova = self.atividade()
        self.nota(prova)

        with self.assertRaises(RestrictedError):
            prova.delete()

    def test_excluir_a_turma_remove_modulos_atividades_notas_e_materiais(self):
        prova = self.atividade()
        self.nota(prova)
        ClassroomMaterial.objects.create(
            turma=self.turma, modulo=self.modulo, titulo="M",
            arquivo="materiais/teste.pdf")
        self.login(self.professor)

        response = self.client.delete(
            self.url("classrooms-professor-detail", self.turma.id))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Module.objects.filter(turma_id=self.turma.id).exists())
        self.assertFalse(Activity.objects.filter(pk=prova.pk).exists())
        self.assertFalse(Grade.objects.filter(turma_id=self.turma.id).exists())
        self.assertFalse(
            ClassroomMaterial.objects.filter(turma_id=self.turma.id).exists())


class RegrasDeModeloTests(BaseAtividadesTestCase):
    def nova(self, **extra):
        dados = {
            "turma": self.turma,
            "modulo": self.modulo,
            "titulo": "Prova",
            "tipo": Activity.TIPO_PROVA,
            "pontuada": True,
            "peso": Decimal("5.00"),
            "data_entrega": self.prazo,
        }
        dados.update(extra)
        return Activity(**dados)

    def test_atividade_valida_passa(self):
        self.nova().full_clean()
        self.nova(tipo=Activity.TIPO_LISTA, pontuada=False, peso=None,
                  data_entrega=None).full_clean()
        self.nova(tipo=Activity.TIPO_RECUPERACAO, peso=Decimal("10.00"),
                  modo_recuperacao=Activity.RECUPERACAO_UNIDADE).full_clean()
        self.nova(tipo=Activity.TIPO_TRABALHO, max_revisoes=3).full_clean()
        self.nova(quantidade_sorteio=10).full_clean()

    def test_atividades_invalidas_sao_rejeitadas(self):
        casos = {
            "prova sem pontuação": {"pontuada": False, "peso": None},
            "lista sem pontuação com peso": {
                "tipo": Activity.TIPO_LISTA, "pontuada": False},
            "peso zero": {"peso": Decimal("0")},
            "peso acima de 10": {"peso": Decimal("10.01")},
            "pontuada sem data de entrega": {"data_entrega": None},
            "início depois da entrega": {
                "data_inicio": self.prazo + timedelta(days=1)},
            "revisão em prova": {"max_revisoes": 1},
            "sorteio em trabalho": {
                "tipo": Activity.TIPO_TRABALHO, "quantidade_sorteio": 3},
            "sorteio zero": {"quantidade_sorteio": 0},
            "recuperação sem modo": {
                "tipo": Activity.TIPO_RECUPERACAO,
                "peso": Decimal("10.00")},
            "modo de recuperação em prova": {
                "modo_recuperacao": Activity.RECUPERACAO_PROVA},
            "módulo de outra turma": {"modulo": self.modulo_outra_turma},
            "sem título": {"titulo": ""},
            "tipo inexistente": {"tipo": "material"},
        }
        for nome, extra in casos.items():
            with self.subTest(caso=nome):
                with self.assertRaises(ValidationError):
                    self.nova(**extra).full_clean()

    def test_nota_nao_pode_passar_do_peso_nem_ser_de_outra_turma(self):
        prova = self.atividade(peso=Decimal("6.00"))
        alheia = Activity.objects.create(
            turma=self.outra_turma,
            modulo=self.modulo_outra_turma,
            titulo="Alheia",
            tipo=Activity.TIPO_PROVA,
            peso=Decimal("5.00"),
            data_entrega=self.prazo,
        )

        Grade(aluno=self.aluno, turma=self.turma, atividade=prova,
              valor=Decimal("6.00")).full_clean(validate_unique=False)
        with self.assertRaises(ValidationError):
            Grade(aluno=self.aluno, turma=self.turma, atividade=prova,
                  valor=Decimal("6.01")).full_clean(validate_unique=False)
        with self.assertRaises(ValidationError):
            Grade(aluno=self.aluno, turma=self.turma, atividade=alheia,
                  valor=Decimal("1.00")).full_clean(validate_unique=False)

    def test_anotacao_de_pesos_por_modulo(self):
        self.atividade(titulo="Prova", peso=Decimal("6.00"))
        self.atividade(titulo="Trabalho", tipo=Activity.TIPO_TRABALHO,
                       peso=Decimal("1.00"))
        self.atividade(titulo="Inativa", tipo=Activity.TIPO_TESTE,
                       peso=Decimal("2.00"), ativo=False)
        self.atividade(titulo="Rec", tipo=Activity.TIPO_RECUPERACAO,
                       peso=Decimal("10.00"), modo_recuperacao="unidade")
        vazio = Module.objects.create(
            turma=self.turma, nome="Vazio", ordem=2)

        modulos = anotar_pesos_distribuidos(
            Module.objects.filter(turma=self.turma)).in_bulk()

        self.assertEqual(modulos[self.modulo.id].pesos_total, Decimal("7.00"))
        self.assertIsNone(modulos[vazio.id].pesos_total)
