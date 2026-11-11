from django.core.exceptions import ValidationError
from django.db import models

from ..storage import armazenamento_privado, caminho_material
from .classroom import Classroom
from .module import Module


# Representa um material complementar (PDF, tabela etc.) enviado pelo professor, sem nota ou status.
class ClassroomMaterial(models.Model):
    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="materiais",
    )
    modulo = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        related_name="materiais",
        blank=True,
        null=True,
    )
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    arquivo = models.FileField(
        upload_to=caminho_material,
        storage=armazenamento_privado,
    )
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        db_table = "classroom_materials"

    def __str__(self):
        return f"{self.turma.nome} - {self.titulo}"

    def clean(self):
        if not self.titulo:
            raise ValidationError("Título do material é obrigatório.")

        if self.modulo_id and self.modulo.turma_id != self.turma_id:
            raise ValidationError("O módulo não pertence a esta turma.")
