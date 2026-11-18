from django.core.exceptions import ValidationError
from django.db import models

from .activity import Activity
from .classroom import Classroom
from .module import Module


def normalizar_texto(texto):
    """Remove espaços extras e ignora maiúsculas para comparar alternativas."""
    return " ".join((texto or "").split()).casefold()


# Representa uma questão de múltipla escolha (de 2 a 5 alternativas) do banco de um módulo.
class Question(models.Model):
    DIFICULDADE_FACIL = "facil"
    DIFICULDADE_MEDIO = "medio"
    DIFICULDADE_DIFICIL = "dificil"

    DIFICULDADES = [
        (DIFICULDADE_FACIL, "Fácil"),
        (DIFICULDADE_MEDIO, "Médio"),
        (DIFICULDADE_DIFICIL, "Difícil"),
    ]

    CAMPOS_ALTERNATIVAS = (
        "alternativa_a",
        "alternativa_b",
        "alternativa_c",
        "alternativa_d",
        "alternativa_e",
    )

    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="questoes",
    )
    # RESTRICT impede apagar o módulo isolado, mas permite a exclusão em cascata da turma.
    modulo = models.ForeignKey(
        Module,
        on_delete=models.RESTRICT,
        related_name="questoes",
    )
    enunciado = models.TextField()
    alternativa_a = models.TextField()
    alternativa_b = models.TextField()
    alternativa_c = models.TextField(blank=True, default="")
    alternativa_d = models.TextField(blank=True, default="")
    alternativa_e = models.TextField(blank=True, default="")
    # Guarda o texto exato da alternativa correta, o que permite embaralhar as alternativas.
    resposta_correta = models.TextField()
    justificativa = models.TextField(blank=True, default="")
    dificuldade = models.CharField(
        max_length=10,
        choices=DIFICULDADES,
        default=DIFICULDADE_MEDIO,
    )
    # Questões de prova e teste só entram no banco se o professor optar; as de lista sempre entram.
    no_banco = models.BooleanField(default=True)
    atividade_origem = models.ForeignKey(
        Activity,
        on_delete=models.SET_NULL,
        related_name="questoes_criadas",
        blank=True,
        null=True,
    )
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "questions"
        indexes = [
            models.Index(
                fields=["modulo", "no_banco", "ativo"],
                name="question_mod_banco_ativo_idx",
            )
        ]

    def __str__(self):
        return f"{self.modulo.nome} - {self.enunciado[:50]}"

    def alternativas(self):
        """Textos das alternativas preenchidas, na ordem A a E."""
        textos = (getattr(self, campo) or "" for campo in self.CAMPOS_ALTERNATIVAS)
        return [texto.strip() for texto in textos if texto.strip()]

    def clean(self):
        # A normalização garante que o texto gravado seja idêntico ao comparado na correção.
        self.enunciado = (self.enunciado or "").strip()
        self.resposta_correta = (self.resposta_correta or "").strip()
        self.justificativa = (self.justificativa or "").strip()
        for campo in self.CAMPOS_ALTERNATIVAS:
            setattr(self, campo, (getattr(self, campo) or "").strip())

        if not self.enunciado:
            raise ValidationError("O enunciado da questão é obrigatório.")

        if self.modulo_id and self.modulo.turma_id != self.turma_id:
            raise ValidationError("O módulo não pertence a esta turma.")

        if (
            self.atividade_origem_id
            and self.atividade_origem.turma_id != self.turma_id
        ):
            raise ValidationError("A atividade de origem não pertence a esta turma.")

        textos = [getattr(self, campo) for campo in self.CAMPOS_ALTERNATIVAS]
        if not textos[0] or not textos[1]:
            raise ValidationError(
                "A questão precisa ter ao menos as alternativas A e B.")

        primeira_vazia = next(
            (indice for indice, texto in enumerate(textos) if not texto),
            None,
        )
        if primeira_vazia is not None and any(textos[primeira_vazia:]):
            raise ValidationError(
                "As alternativas devem ser preenchidas em sequência, sem lacunas.")

        preenchidas = [texto for texto in textos if texto]
        if len({normalizar_texto(texto) for texto in preenchidas}) != len(preenchidas):
            raise ValidationError("As alternativas não podem ser repetidas.")

        if self.resposta_correta not in preenchidas:
            raise ValidationError(
                "A resposta correta deve ser exatamente o texto de uma das alternativas.")


# Vincula uma questão a uma atividade (questões fixas ou pool de sorteio), com ordem de exibição.
class ActivityQuestion(models.Model):
    atividade = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="atividade_questoes",
    )
    questao = models.ForeignKey(
        Question,
        on_delete=models.RESTRICT,
        related_name="usos_em_atividades",
    )
    ordem = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "created_at"]
        db_table = "activity_questions"
        constraints = [
            models.UniqueConstraint(
                fields=["atividade", "questao"],
                name="unique_question_per_activity",
            ),
            models.UniqueConstraint(
                fields=["atividade", "ordem"],
                name="unique_question_order_per_activity",
            ),
        ]

    def __str__(self):
        return f"{self.atividade.titulo} - questão {self.ordem}"

    def clean(self):
        if self.ordem is not None and self.ordem < 1:
            raise ValidationError("A ordem da questão deve ser maior que zero.")

        if self.atividade_id and self.questao_id:
            if self.atividade.turma_id != self.questao.turma_id:
                raise ValidationError(
                    "A questão não pertence à turma da atividade.")

            if self.atividade.tipo not in Activity.TIPOS_COM_QUESTOES:
                raise ValidationError(
                    "Este tipo de atividade não utiliza questões.")
