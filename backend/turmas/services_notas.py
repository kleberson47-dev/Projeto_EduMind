from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from django.utils import timezone

from .models import Activity, Module

PESO_TOTAL_MODULO = Decimal("10")
CENTAVOS = Decimal("0.01")
# Tipos que dividem os 10 pontos do módulo; a recuperação fica de fora.
TIPOS_COM_PESO_NO_MODULO = (
    Activity.TIPO_TRABALHO,
    Activity.TIPO_PROVA,
    Activity.TIPO_TESTE,
    Activity.TIPO_LISTA,
)


def arredondar_nota(valor):
    """Arredonda para 2 casas; valores terminados em ,99 sobem para o inteiro seguinte."""
    nota = Decimal(str(valor)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    if nota % 1 == Decimal("0.99"):
        nota = nota.to_integral_value(rounding=ROUND_CEILING)
    return nota.quantize(CENTAVOS)


def definir_modo_distribuicao(modulo, modo):
    """Define uma única vez o critério de distribuição de pontos do módulo."""
    modos_validos = {valor for valor, _ in Module.MODOS_DISTRIBUICAO}
    if modo not in modos_validos:
        raise ValidationError("Critério de distribuição inválido.")

    if not modulo.ativo:
        raise ValidationError("Não é possível alterar um módulo inativo.")

    # O filtro por nulo torna a definição atômica: só a primeira escolha é gravada.
    atualizados = Module.objects.filter(
        pk=modulo.pk,
        modo_distribuicao__isnull=True,
    ).update(modo_distribuicao=modo, updated_at=timezone.now())

    if not atualizados:
        raise ValidationError(
            "O critério de distribuição deste módulo já foi definido e não pode ser alterado."
        )

    modulo.modo_distribuicao = modo
    return modulo


def pesos_distribuidos(modulo, excluir_atividade_id=None):
    """Soma os pesos das atividades ativas e pontuadas do módulo, exceto a recuperação."""
    atividades = Activity.objects.filter(
        modulo=modulo,
        ativo=True,
        pontuada=True,
        peso__isnull=False,
    ).exclude(tipo=Activity.TIPO_RECUPERACAO)

    if excluir_atividade_id is not None:
        atividades = atividades.exclude(pk=excluir_atividade_id)

    return atividades.aggregate(total=Sum("peso"))["total"] or Decimal("0")


def anotar_pesos_distribuidos(modulos):
    """Anota `pesos_total` em uma consulta de módulos, evitando consultas por item nos serializers."""
    return modulos.annotate(
        pesos_total=Sum(
            "atividades__peso",
            filter=Q(
                atividades__ativo=True,
                atividades__pontuada=True,
                atividades__tipo__in=TIPOS_COM_PESO_NO_MODULO,
            ),
        )
    )


def _normalizar_peso(valor):
    try:
        return Decimal(str(valor)).quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ValidationError("Peso inválido.") from exc


def peso_para_nova_atividade(
    modulo,
    tipo,
    pontuada,
    peso_informado=None,
    atividade_id=None,
    ativa=True,
):
    """Calcula o peso da atividade conforme o critério de distribuição do módulo."""
    if not pontuada:
        if peso_informado is not None:
            raise ValidationError(
                "Atividades sem pontuação não podem ter peso.")
        return None

    peso_maximo = PESO_TOTAL_MODULO.quantize(CENTAVOS)

    if tipo == Activity.TIPO_RECUPERACAO:
        return peso_maximo

    if modulo.modo_distribuicao is None:
        raise ValidationError(
            "Defina o critério de distribuição de pontos do módulo antes de criar atividades pontuadas."
        )

    if modulo.modo_distribuicao == Module.DISTRIBUICAO_MEDIA:
        if peso_informado is not None and _normalizar_peso(peso_informado) != peso_maximo:
            raise ValidationError(
                "No critério de média, todas as atividades valem 10.")
        return peso_maximo

    if peso_informado is None:
        raise ValidationError("Informe o peso da atividade.")

    peso = _normalizar_peso(peso_informado)
    if not 0 < peso <= PESO_TOTAL_MODULO:
        raise ValidationError("O peso deve ser maior que 0 e até 10.")

    if ativa:
        restante = PESO_TOTAL_MODULO - \
            pesos_distribuidos(modulo, atividade_id)
        if peso > restante:
            raise ValidationError(
                f"O peso excede os pontos disponíveis no módulo (restam {restante})."
            )

    return peso


def peso_bloqueado(atividade):
    """O peso não pode mais mudar quando já existem notas lançadas na atividade."""
    return atividade.notas.exists()
