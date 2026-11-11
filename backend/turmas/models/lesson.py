from django.core.exceptions import ValidationError
from django.db import models

from .classroom import Classroom
from .module import Module


# Representa uma aula dentro de uma turma, com ordenação para o conteúdo didático.
class Lesson(models.Model):
    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="aulas",
    )
    modulo = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        related_name="aulas",
        blank=True,
        null=True,
    )
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    ordem = models.PositiveIntegerField(default=1)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "created_at"]
        db_table = "lessons"
        constraints = [
            models.UniqueConstraint(
                fields=["turma", "ordem"],
                name="unique_lesson_order_per_classroom",
            )
        ]

    def __str__(self):
        return f"{self.turma.nome} - {self.titulo}"

    def clean(self):
        if not self.titulo:
            raise ValidationError("Título da aula é obrigatório.")

        if self.modulo_id and self.modulo.turma_id != self.turma_id:
            raise ValidationError("O módulo não pertence a esta turma.")


# Representa uma seção dentro de uma aula para separar blocos de conteúdo.
class LessonSection(models.Model):
    aula = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="secoes",
    )
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    ordem = models.PositiveIntegerField(default=1)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "created_at"]
        db_table = "lesson_sections"
        constraints = [
            models.UniqueConstraint(
                fields=["aula", "ordem"],
                name="unique_section_order_per_lesson",
            )
        ]

    def __str__(self):
        return f"{self.aula.titulo} - {self.titulo}"

    def clean(self):
        if not self.titulo:
            raise ValidationError("Título da seção é obrigatório.")


# Representa um bloco de conteúdo dentro de uma seção, como texto, imagem, vídeo ou tabela.
class LessonBlock(models.Model):
    TIPO_TEXTO = "texto"
    TIPO_IMAGEM = "imagem"
    TIPO_VIDEO = "video"
    TIPO_TABELA = "tabela"
    TIPO_LISTA = "lista"

    TIPOS_BLOCO = [
        (TIPO_TEXTO, "Texto"),
        (TIPO_IMAGEM, "Imagem"),
        (TIPO_VIDEO, "Vídeo"),
        (TIPO_TABELA, "Tabela"),
        (TIPO_LISTA, "Lista"),
    ]

    secao = models.ForeignKey(
        LessonSection,
        on_delete=models.CASCADE,
        related_name="blocos",
    )
    tipo = models.CharField(
        max_length=20, choices=TIPOS_BLOCO, default=TIPO_TEXTO)
    titulo = models.CharField(max_length=255, blank=True, default="")
    conteudo = models.TextField(blank=True, default="")
    arquivo_imagem = models.ImageField(
        upload_to="aulas/imagens/%Y/%m/",
        blank=True,
    )
    url_imagem = models.URLField(blank=True, default="")
    arquivo_video = models.FileField(
        upload_to="aulas/videos/%Y/%m/",
        blank=True,
    )
    url_video = models.URLField(blank=True, default="")
    tabela_json = models.JSONField(blank=True, null=True, default=dict)
    ordem = models.PositiveIntegerField(default=1)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ordem", "created_at"]
        db_table = "lesson_blocks"
        constraints = [
            models.UniqueConstraint(
                fields=["secao", "ordem"],
                name="unique_block_order_per_section",
            )
        ]

    def __str__(self):
        return f"{self.secao.titulo} - {self.tipo}"

    def clean(self):
        if self.tipo == self.TIPO_TEXTO and not self.conteudo:
            raise ValidationError("Blocos de texto precisam de conteúdo.")

        if self.tipo == self.TIPO_IMAGEM:
            if not self.arquivo_imagem:
                raise ValidationError(
                    "Blocos de imagem precisam de um arquivo de imagem."
                )

        if self.tipo == self.TIPO_VIDEO:
            tem_arquivo = bool(self.arquivo_video)
            tem_url = bool(self.url_video)

            if tem_arquivo and tem_url:
                raise ValidationError(
                    "Blocos de vídeo não podem ter arquivo e URL ao mesmo tempo."
                )

            if not tem_arquivo and not tem_url:
                raise ValidationError(
                    "Blocos de vídeo precisam de um arquivo ou URL válidos."
                )

        if self.tipo == self.TIPO_TABELA and not self.tabela_json:
            raise ValidationError(
                "Blocos de tabela precisam de dados em JSON.")
