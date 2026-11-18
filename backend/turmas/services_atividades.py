from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import Max

from .models import Activity, Module
from .services_notas import peso_bloqueado, peso_para_nova_atividade

RESULTADO_EXCLUIDA = "excluida"
RESULTADO_DESATIVADA = "desativada"

# Campos que o professor pode informar; o restante (turma, módulo, publicação) é controlado pelos services.
CAMPOS_EDITAVEIS = (
    "titulo",
    "descricao",
    "tipo",
    "pontuada",
    "peso",
    "data_inicio",
    "data_entrega",
    "max_revisoes",
    "quantidade_sorteio",
    "modo_recuperacao",
    "ativo",
)


def _filtrar_campos(dados):
    return {campo: dados[campo] for campo in CAMPOS_EDITAVEIS if campo in dados}


def _validar_modulo_da_turma(turma, modulo):
    if modulo.turma_id != turma.id:
        raise ValidationError("O módulo não pertence a esta turma.")

    if not modulo.ativo:
        raise ValidationError("O módulo está inativo.")


def criar_modulo(turma, nome):
    """Cria um módulo no fim da sequência de módulos da turma."""
    nome = (nome or "").strip()
    if not nome:
        raise ValidationError("O nome do módulo é obrigatório.")

    try:
        with transaction.atomic():
            maior_ordem = turma.modulos.aggregate(
                maior=Max("ordem"))["maior"] or 0
            return Module.objects.create(
                turma=turma,
                nome=nome,
                ordem=maior_ordem + 1,
            )
    except IntegrityError as exc:
        raise ValidationError(
            "Não foi possível criar o módulo. Tente novamente.") from exc


def desativar_modulo(modulo):
    """Desativa o módulo, desde que não tenha atividades ativas."""
    if modulo.atividades.filter(ativo=True).exists():
        raise ValidationError(
            "Não é possível desativar um módulo com atividades ativas.")

    modulo.ativo = False
    modulo.save(update_fields=["ativo", "updated_at"])
    return modulo


def criar_atividade(turma, modulo, dados):
    """Cria uma atividade não publicada, definindo o peso conforme o critério do módulo."""
    campos = _filtrar_campos(dados)
    tipo = campos.get("tipo")

    if tipo not in dict(Activity.TIPOS_ATIVIDADE):
        raise ValidationError("Informe um tipo de atividade válido.")

    peso_informado = campos.pop("peso", None)

    with transaction.atomic():
        # O bloqueio evita que duas criações simultâneas ultrapassem os 10 pontos do módulo.
        modulo = Module.objects.select_for_update().get(pk=modulo.pk)
        _validar_modulo_da_turma(turma, modulo)

        peso = peso_para_nova_atividade(
            modulo,
            tipo,
            campos.get("pontuada", True),
            peso_informado,
            ativa=campos.get("ativo", True),
        )

        atividade = Activity(
            turma=turma,
            modulo=modulo,
            peso=peso,
            publicado=False,
            **campos,
        )
        atividade.full_clean()
        atividade.save()

    return atividade


def atualizar_atividade(atividade, dados):
    """Atualiza a atividade; tipo e módulo são imutáveis e o peso trava após haver notas."""
    campos = _filtrar_campos(dados)

    if campos.pop("tipo", atividade.tipo) != atividade.tipo:
        raise ValidationError(
            "O tipo da atividade não pode ser alterado depois de criada.")

    pontuada = campos.get("pontuada", atividade.pontuada)
    peso_informado = campos.pop("peso", None)
    if peso_informado is None and pontuada:
        peso_informado = atividade.peso

    with transaction.atomic():
        modulo = Module.objects.select_for_update().get(pk=atividade.modulo_id)

        novo_peso = peso_para_nova_atividade(
            modulo,
            atividade.tipo,
            pontuada,
            peso_informado,
            atividade_id=atividade.pk,
            ativa=campos.get("ativo", atividade.ativo),
        )

        mudou_pontuacao = (
            novo_peso != atividade.peso or pontuada != atividade.pontuada
        )
        if mudou_pontuacao and peso_bloqueado(atividade):
            raise ValidationError(
                "O peso e a pontuação não podem ser alterados depois que há notas lançadas."
            )

        for campo, valor in campos.items():
            setattr(atividade, campo, valor)
        atividade.peso = novo_peso

        atividade.full_clean()
        atividade.save()

    return atividade


def publicar_atividade(atividade):
    """Torna a atividade visível aos alunos, validando que ela está pronta."""
    if not atividade.ativo or not atividade.modulo.ativo:
        raise ValidationError("Atividades inativas não podem ser publicadas.")

    if atividade.publicado:
        raise ValidationError("A atividade já está publicada.")

    if atividade.pontuada and atividade.peso is None:
        raise ValidationError("A atividade pontuada precisa ter um peso.")

    atividade.full_clean()
    atividade.publicado = True
    atividade.save(update_fields=["publicado", "updated_at"])
    return atividade


def desativar_ou_excluir_atividade(atividade):
    """Exclui a atividade sem histórico; caso contrário apenas a desativa."""
    if peso_bloqueado(atividade):
        atividade.ativo = False
        atividade.save(update_fields=["ativo", "updated_at"])
        return RESULTADO_DESATIVADA

    atividade.delete()
    return RESULTADO_EXCLUIDA