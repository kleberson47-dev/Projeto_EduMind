from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


# Representa a turma/disciplina criada pelo professor.
class Classroom(models.Model):
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="turmas_criadas",
        limit_choices_to={"role": "professor"},
    )
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    codigo_acesso = models.CharField(max_length=30, unique=True)
    criterios_avaliacao = models.TextField(blank=True, default="")
    regras = models.TextField(blank=True, default="")
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        db_table = "classrooms"

    def __str__(self):
        return self.nome

    def clean(self):
        if not self.codigo_acesso:
            raise ValidationError("Código de acesso é obrigatório.")
        if not self.nome:
            raise ValidationError("Nome da turma é obrigatório.")


# Representa uma atividade ou tarefa vinculada a uma turma.
class Activity(models.Model):
    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="atividades",
    )
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, default="")
    tipo = models.CharField(
        max_length=50,
        default="atividade",
        choices=[
            ("atividade", "Atividade"),
            ("trabalho", "Trabalho"),
            ("prova", "Prova"),
            ("material", "Material"),
        ],
    )
    data_entrega = models.DateField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data_entrega", "-created_at"]
        db_table = "activities"

    def __str__(self):
        return f"{self.turma.nome} - {self.titulo}"

    def clean(self):
        if not self.titulo:
            raise ValidationError("Título da atividade é obrigatório.")


# Representa a nota atribuída a um aluno em uma atividade de uma turma.
class Grade(models.Model):
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
    atividade = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="notas",
        blank=True,
        null=True,
    )
    valor = models.DecimalField(max_digits=5, decimal_places=2)
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


# Relaciona um aluno a uma turma e controla se a matrícula está ativa.
class Enrollment(models.Model):
    aluno = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="matriculas",
        limit_choices_to={"role": "aluno"},
    )
    turma = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    ativo = models.BooleanField(default=True)
    data_entrada = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["aluno", "turma"],
                name="unique_enrollment_per_student_classroom",
            )
        ]
        ordering = ["-data_entrada"]
        db_table = "enrollments"

    def __str__(self):
        return f"{self.aluno.nome} -> {self.turma.nome}"

    def clean(self):
        if self.aluno.role != "aluno":
            raise ValidationError(
                "Só pode haver matrícula para usuários com perfil de aluno.")
