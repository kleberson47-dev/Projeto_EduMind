import random
import string

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Classroom, Enrollment, Lesson, LessonBlock, LessonSection


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


def _reordenar_itens_por_ordem(queryset, item_id, nova_ordem):
    """Reordena itens de um mesmo nível sem duplicar a ordem dentro do grupo."""
    itens = list(queryset.order_by("ordem"))

    if not itens:
        raise ValidationError("Não há itens para reordenar.")

    item_encontrado = None
    indice_item = None

    for indice, item in enumerate(itens):
        if item.pk == item_id:
            item_encontrado = item
            indice_item = indice
            break

    if item_encontrado is None:
        raise ValidationError("Item não encontrado para reordenar.")

    if nova_ordem is None or nova_ordem < 1:
        raise ValidationError("A nova ordem deve ser um número maior que zero.")

    ordem_final = min(int(nova_ordem), len(itens))
    itens_sem_item = [item for item in itens if item.pk != item_id]
    itens_reordenados = itens_sem_item[:]
    itens_reordenados.insert(ordem_final - 1, item_encontrado)

    with transaction.atomic():
        temp_base = max((item.ordem for item in itens), default=0) + 1000
        for indice, item in enumerate(itens):
            item.ordem = temp_base + indice + 1
            item.save(update_fields=["ordem"])

        for indice, item in enumerate(itens_reordenados, start=1):
            item.ordem = indice
            item.save(update_fields=["ordem"])

    return itens_reordenados


def reordenar_aulas(turma_id, lesson_id, nova_ordem):
    """Move uma aula para uma nova posição dentro da mesma turma."""
    queryset = Lesson.objects.filter(turma_id=turma_id).order_by("ordem")
    return _reordenar_itens_por_ordem(queryset, lesson_id, nova_ordem)


def reordenar_secoes(aula_id, section_id, nova_ordem):
    """Move uma seção para uma nova posição dentro da mesma aula."""
    queryset = LessonSection.objects.filter(aula_id=aula_id).order_by("ordem")
    return _reordenar_itens_por_ordem(queryset, section_id, nova_ordem)


def reordenar_blocos(secao_id, block_id, nova_ordem):
    """Move um bloco para uma nova posição dentro da mesma seção."""
    queryset = LessonBlock.objects.filter(secao_id=secao_id).order_by("ordem")
    return _reordenar_itens_por_ordem(queryset, block_id, nova_ordem)
