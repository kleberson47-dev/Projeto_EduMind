from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .classroom import Classroom
from .module import Module


# Representa uma atividade avaliativa ou de acompanhamento vinculada a um módulo da turma.
class Activity(models.Model):
    TIPO_TRABALHO = "trabalho"
    TIPO_PROVA = "prova"
    TIPO_TESTE = "teste"
    TIPO_LISTA = "lista"
    TIPO_RECUPERACAO = "recuperacao"

    TIPOS_ATIVIDADE = [
        (TIPO_TRABALHO, "Trabalho"),
        (TIPO_PROVA, "Prova"),
        (TIPO_TESTE, "Teste"),
        (TIPO_LISTA, "Lista"),
        (TIPO_RECUPERACAO, "Recuperação"),
    ]

    # Somente a lista pode ser cadastrada sem pontuação.
    TIPOS_SEMPRE_PONTUADOS = (
        TIPO_TRABALHO,
        TIPO_PROVA,
        TIPO_TESTE,
        TIPO_RECUPERACAO,
    )
    TIPOS_COM_QUESTOES = (
        TIPO_PROVA,
        TIPO_TESTE,
        TIPO_LISTA,
        TIPO_RECUPERACAO,
    )

    RECUPERACAO_PROVA = "prova"
    RECUPERACAO_UNIDADE = "unidade"

    MODOS_RECUPERACAO = [
        (RECUPERACAO_PROVA, "Substitui a prova com menor nota"),
        (RECUPERACAO_UNIDADE, "Vale a nota da unidade"),
    ]

    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="atividades",
    )
    # RESTRICT impede apagar o módulo isolado, mas permite a exclusão em cascata da turma.
    modulo = models.ForeignKey(
        Module,
        on_delete=models.RESTRICT,
        related_name="atividades",
    )
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    tipo = models.CharField(max_length=50, choices=TIPOS_ATIVIDADE)
    pontuada = models.BooleanField(default=True)
    # Definido apenas pelo service de notas, conforme o modo de distribuição do módulo.
    peso = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
    )
    data_inicio = models.DateField(blank=True, null=True)
    data_entrega = models.DateField(blank=True, null=True)
    publicado = models.BooleanField(default=False)
    max_revisoes = models.PositiveSmallIntegerField(default=0)
    quantidade_sorteio = models.PositiveSmallIntegerField(
        blank=True, null=True)
    modo_recuperacao = models.CharField(
        max_length=10,
        choices=MODOS_RECUPERACAO,
        blank=True,
        null=True,
    )
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data_entrega", "-created_at"]
        db_table = "activities"
        indexes = [
            models.Index(
                fields=["turma", "modulo", "tipo"],
                name="activity_turma_modulo_tipo_idx",
            )
        ]

    def __str__(self):
        return f"{self.turma.nome} - {self.titulo}"

    def clean(self):
        if not self.titulo:
            raise ValidationError("Título da atividade é obrigatório.")

        if self.modulo_id and self.modulo.turma_id != self.turma_id:
            raise ValidationError("O módulo não pertence a esta turma.")

        if self.tipo in self.TIPOS_SEMPRE_PONTUADOS and not self.pontuada:
            raise ValidationError(
                "Este tipo de atividade sempre possui pontuação.")

        if not self.pontuada and self.peso is not None:
            raise ValidationError(
                "Atividades sem pontuação não podem ter peso.")

        if self.peso is not None and not 0 < self.peso <= 10:
            raise ValidationError("O peso deve ser maior que 0 e até 10.")

        if self.data_entrega is None and self.pontuada:
            raise ValidationError(
                "A data de entrega é obrigatória para atividades pontuadas.")

        if (
            self.data_inicio is not None
            and self.data_entrega is not None
            and self.data_inicio > self.data_entrega
        ):
            raise ValidationError(
                "A data de início não pode ser posterior à data de entrega.")

        if self.max_revisoes and self.tipo != self.TIPO_TRABALHO:
            raise ValidationError(
                "Revisões só podem ser habilitadas em trabalhos.")

        if self.quantidade_sorteio is not None:
            if self.tipo not in self.TIPOS_COM_QUESTOES:
                raise ValidationError(
                    "Este tipo de atividade não utiliza questões.")
            if self.quantidade_sorteio < 1:
                raise ValidationError(
                    "A quantidade de questões sorteadas deve ser maior que zero.")

        if self.tipo == self.TIPO_RECUPERACAO and not self.modo_recuperacao:
            raise ValidationError(
                "Informe como a recuperação será aplicada.")

        if self.tipo != self.TIPO_RECUPERACAO and self.modo_recuperacao:
            raise ValidationError(
                "O modo de recuperação só se aplica a atividades de recuperação.")


# Representa a nota atribuída a um aluno em uma atividade de uma turma.
class Grade(models.Model):
    ORIGEM_AUTOMATICA = "automatica"
    ORIGEM_MANUAL = "manual"

    ORIGENS = [
        (ORIGEM_AUTOMATICA, "Correção automática"),
        (ORIGEM_MANUAL, "Lançamento do professor"),
    ]

    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notas",
        limit_choices_to={"role": "aluno"},
    )
    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="notas",
    )
    # RESTRICT impede apagar a atividade isolada, mas permite a exclusão em cascata da turma.
    atividade = models.ForeignKey(
        Activity,
        on_delete=models.RESTRICT,
        related_name="notas",
    )
    valor = models.DecimalField(max_digits=5, decimal_places=2)
    origem = models.CharField(
        max_length=15, choices=ORIGENS, default=ORIGEM_MANUAL)
    # Guarda a nota calculada pelo sistema quando o professor a ajusta manualmente.
    valor_automatico = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
    )
    observacao = models.TextField(blank=True, default="")
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "grades"
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "turma", "atividade"],
                name="unique_grade_per_student_classroom_activity",
            )
        ]

    def __str__(self):
        return f"{self.aluno.nome} - {self.turma.nome} - {self.valor}"

    def clean(self):
        if self.valor < 0:
            raise ValidationError("A nota não pode ser menor que zero.")
        if self.valor > 10:
            raise ValidationError("A nota deve estar entre 0 e 10.")

        if self.atividade_id:
            if self.atividade.turma_id != self.turma_id:
                raise ValidationError("A atividade não pertence a esta turma.")
            if self.atividade.peso is not None and self.valor > self.atividade.peso:
                raise ValidationError(
                    "A nota não pode ser maior que o peso da atividade.")
