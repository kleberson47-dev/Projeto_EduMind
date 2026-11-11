from django.core.exceptions import ValidationError
from django.db import models

from .classroom import Classroom


# Representa uma unidade/módulo da turma, que agrupa aulas, atividades e questões.
class Module(models.Model):
    DISTRIBUICAO_MEDIA = "media"
    DISTRIBUICAO_LIVRE = "livre"

    MODOS_DISTRIBUICAO = [
        (DISTRIBUICAO_MEDIA, "Todas valem 10 (média simples)"),
        (DISTRIBUICAO_LIVRE, "Distribuição livre de pesos"),
    ]

    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="modulos",
    )
    nome = models.CharField(max_length=255)
    ordem = models.PositiveIntegerField(default=1)
    # Nulo até o professor escolher; depois de definido não pode mais ser alterado.
    modo_distribuicao = models.CharField(
        max_length=10,
        choices=MODOS_DISTRIBUICAO,
        blank=True,
        null=True,
    )
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "created_at"]
        db_table = "modules"
        constraints = [
            models.UniqueConstraint(
                fields=["turma", "ordem"],
                name="unique_module_order_per_classroom",
            )
        ]

    def __str__(self):
        return f"{self.turma.nome} - {self.nome}"

    def clean(self):
        if not self.nome:
            raise ValidationError("Nome do módulo é obrigatório.")
