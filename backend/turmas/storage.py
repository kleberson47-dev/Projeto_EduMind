from django.conf import settings
from django.core.files.storage import FileSystemStorage


# Callable para o Django não gravar o caminho local da máquina nas migrations.
def armazenamento_privado():
    """Storage fora do MEDIA_ROOT público; o acesso é feito apenas por views autenticadas."""
    return FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT)


def caminho_entrega(instance, filename):
    """Organiza as entregas por turma, atividade e aluno."""
    atividade = instance.atividade
    return (
        f"entregas/turma_{atividade.turma_id}/atividade_{atividade.pk}/"
        f"aluno_{instance.aluno_id}/{filename}"
    )


def caminho_material(instance, filename):
    """Organiza os materiais complementares por turma."""
    return f"materiais/turma_{instance.turma_id}/{filename}"
