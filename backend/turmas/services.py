import random
import string

from django.core.exceptions import ValidationError

from .models import Classroom, Enrollment


def gerar_codigo_acesso(tamanho=8):
    """Gera um código único para acesso da turma."""
    caracteres = string.ascii_uppercase + string.digits
    return "".join(random.choice(caracteres) for _ in range(tamanho))


def validar_professor(usuario):
    """Valida se o usuário autenticado possui perfil de professor."""
    if not usuario or getattr(usuario, "role", None) != "professor":
        raise ValidationError(
            "Apenas professores podem criar ou gerenciar turmas.")


def validar_aluno(usuario):
    """Valida se o usuário autenticado possui perfil de aluno."""
    if not usuario or getattr(usuario, "role", None) != "aluno":
        raise ValidationError("Apenas alunos podem entrar em turmas.")


def validar_turma_ativa(turma):
    """Garante que a turma aceita novas matrículas."""
    if turma is None:
        raise ValidationError("Turma não encontrada.")

    if not turma.ativo:
        raise ValidationError(
            "Esta turma está inativa e não aceita novas matrículas.")


def validar_matricula_unica(aluno, turma):
    """Impede matrícula duplicada do mesmo aluno na mesma turma."""
    existe_matricula = Enrollment.objects.filter(
        aluno=aluno, turma=turma).exists()
    if existe_matricula:
        raise ValidationError("Este aluno já está matriculado nesta turma.")


def buscar_turma_por_codigo(codigo_acesso):
    """Busca uma turma ativa pelo código de acesso informado."""
    try:
        return Classroom.objects.get(codigo_acesso=codigo_acesso, ativo=True)
    except Classroom.DoesNotExist as exc:
        raise ValidationError(
            "Código de turma inválido ou turma indisponível.") from exc


def listar_turmas_do_aluno(aluno):
    """Retorna apenas as turmas nas quais o aluno está matriculado e ativo."""
    return Classroom.objects.filter(
        enrollments__aluno=aluno,
        enrollments__ativo=True,
        ativo=True,
    ).distinct().order_by("nome")


def matricular_aluno_por_codigo(aluno, codigo_acesso):
    """Fluxo principal de entrada do aluno em uma turma pelo código."""
    validar_aluno(aluno)

    turma = buscar_turma_por_codigo(codigo_acesso)
    validar_turma_ativa(turma)
    validar_matricula_unica(aluno, turma)

    matricula = Enrollment.objects.create(aluno=aluno, turma=turma, ativo=True)
    return matricula


def criar_turma_para_professor(professor, nome, descricao="", criterios_avaliacao="", regras=""):
    """Cria uma nova turma vinculada ao professor autenticado."""
    validar_professor(professor)

    if not nome or not nome.strip():
        raise ValidationError("O nome da turma é obrigatório.")

    codigo = gerar_codigo_acesso()

    while Classroom.objects.filter(codigo_acesso=codigo).exists():
        codigo = gerar_codigo_acesso()

    turma = Classroom.objects.create(
        professor=professor,
        nome=nome.strip(),
        descricao=descricao or "",
        codigo_acesso=codigo,
        criterios_avaliacao=criterios_avaliacao or "",
        regras=regras or "",
        ativo=True,
    )

    return turma
