from rest_framework import serializers

from ..models import Lesson, LessonBlock, LessonSection


# Serializa cada bloco de conteúdo dentro de uma seção de aula.
class LessonBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonBlock
        fields = [
            "id",
            "secao",
            "tipo",
            "titulo",
            "conteudo",
            "url_imagem",
            "url_video",
            "tabela_json",
            "ordem",
            "ativo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "secao",
            "created_at",
            "updated_at",
        ]

    def validate_tipo(self, value):
        tipos_validos = {tipo for tipo, _ in LessonBlock.TIPOS_BLOCO}
        if value not in tipos_validos:
            raise serializers.ValidationError("Tipo de bloco inválido.")
        return value

    def validate(self, attrs):
        tipo = attrs.get("tipo", getattr(
            self.instance, "tipo", LessonBlock.TIPO_TEXTO))

        if tipo == LessonBlock.TIPO_TEXTO:
            conteudo = attrs.get("conteudo", getattr(
                self.instance, "conteudo", ""))
            if not conteudo.strip():
                raise serializers.ValidationError(
                    "Blocos de texto precisam de conteúdo."
                )

        if tipo == LessonBlock.TIPO_IMAGEM:
            url = attrs.get("url_imagem", getattr(
                self.instance, "url_imagem", ""))
            if not url:
                raise serializers.ValidationError(
                    "Blocos de imagem precisam de uma URL válida."
                )

        if tipo == LessonBlock.TIPO_VIDEO:
            url = attrs.get("url_video", getattr(
                self.instance, "url_video", ""))
            if not url:
                raise serializers.ValidationError(
                    "Blocos de vídeo precisam de uma URL válida."
                )

        if tipo == LessonBlock.TIPO_TABELA:
            tabela = attrs.get("tabela_json", getattr(
                self.instance, "tabela_json", {}))
            if not tabela:
                raise serializers.ValidationError(
                    "Blocos de tabela precisam de dados em JSON."
                )

        return attrs


# Serializa cada seção de uma aula e inclui os blocos em ordem.
class LessonSectionSerializer(serializers.ModelSerializer):
    blocos = LessonBlockSerializer(many=True, read_only=True)

    class Meta:
        model = LessonSection
        fields = [
            "id",
            "aula",
            "titulo",
            "descricao",
            "ordem",
            "ativo",
            "blocos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "aula",
            "blocos",
            "created_at",
            "updated_at",
        ]

    def validate_titulo(self, value):
        titulo = value.strip()
        if not titulo:
            raise serializers.ValidationError(
                "O título da seção é obrigatório.")
        return titulo


# Serializa a aula completa, incluindo suas seções e blocos.
class LessonSerializer(serializers.ModelSerializer):
    secoes = LessonSectionSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "turma",
            "titulo",
            "descricao",
            "ordem",
            "ativo",
            "secoes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "turma",
            "secoes",
            "created_at",
            "updated_at",
        ]

    def validate_titulo(self, value):
        titulo = value.strip()
        if not titulo:
            raise serializers.ValidationError(
                "O título da aula é obrigatório.")
        return titulo
