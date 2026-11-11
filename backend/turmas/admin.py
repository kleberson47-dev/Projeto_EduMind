from django.contrib import admin

from .models import Activity, ClassroomMaterial, Grade, Module


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("nome", "turma", "ordem", "modo_distribuicao", "ativo")
    list_filter = ("modo_distribuicao", "ativo")
    search_fields = ("nome", "turma__nome")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "modulo", "peso",
                    "data_entrega", "publicado", "ativo")
    list_filter = ("tipo", "publicado", "ativo")
    search_fields = ("titulo", "turma__nome")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("aluno", "atividade", "valor", "origem", "ativo")
    list_filter = ("origem", "ativo")


@admin.register(ClassroomMaterial)
class ClassroomMaterialAdmin(admin.ModelAdmin):
    list_display = ("titulo", "turma", "modulo", "ativo")
    list_filter = ("ativo",)
    search_fields = ("titulo", "turma__nome")
