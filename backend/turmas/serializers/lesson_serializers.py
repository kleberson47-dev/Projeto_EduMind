from rest_framework import serializers

from ..models import Lesson, LessonBlock, LessonSection


MAX_SIZE_IMAGEM = 5 * 1024 * 1024
MAX_SIZE_VIDEO = 100 * 1024 * 1024
EXTENSOES_IMAGEM = {"jpg", "jpeg", "png", "gif", "webp"}
EXTENSOES_VIDEO = {"mp4", "webm"}


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
            "arquivo_imagem",
            "url_imagem",
            "arquivo_video",
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

    def validate_arquivo_imagem(self, value):
        if value in (None, ""):
            return value

        extensao = value.name.rsplit(".", 1)[-1].lower()
        if extensao not in EXTENSOES_IMAGEM:
            raise serializers.ValidationError(
                "Formato de imagem inválido. Use JPG, JPEG, PNG, GIF ou WEBP."
            )

        if value.size > MAX_SIZE_IMAGEM:
            raise serializers.ValidationError(
                "A imagem deve ter no máximo 5 MB."
            )

        return value

    def validate_arquivo_video(self, value):
        if value in (None, ""):
            return value

        extensao = value.name.rsplit(".", 1)[-1].lower()
        if extensao not in EXTENSOES_VIDEO:
            raise serializers.ValidationError(
                "Formato de vídeo inválido. Use MP4 ou WEBM."
            )

        if value.size > MAX_SIZE_VIDEO:
            raise serializers.ValidationError(
                "O vídeo deve ter no máximo 100 MB."
            )

        return value

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
            arquivo = attrs.get(
                "arquivo_imagem",
                getattr(self.instance, "arquivo_imagem", None),
            )
            if not arquivo:
                raise serializers.ValidationError(
                    "Blocos de imagem precisam de um arquivo de imagem."
                )

        if tipo == LessonBlock.TIPO_VIDEO:
            arquivo = attrs.get(
                "arquivo_video",
                getattr(self.instance, "arquivo_video", None),
            )
            url = attrs.get("url_video", getattr(self.instance, "url_video", ""))

            if arquivo and url:
                raise serializers.ValidationError(
                    "Blocos de vídeo não podem ter arquivo e URL ao mesmo tempo."
                )

            if not arquivo and not url:
                raise serializers.ValidationError(
                    "Blocos de vídeo precisam de um arquivo ou URL válidos."
                )

        if tipo == LessonBlock.TIPO_TABELA:
            tabela = attrs.get("tabela_json", getattr(
                self.instance, "tabela_json", {}))
            if not tabela:
                raise serializers.ValidationError(
                    "Blocos de tabela precisam de dados em JSON."
                )

        return attrs

    def update(self, instance, validated_data):
        arquivo_imagem = validated_data.get("arquivo_imagem")
        arquivo_video = validated_data.get("arquivo_video")

        if arquivo_imagem is not None and instance.arquivo_imagem:
            instance.arquivo_imagem.delete(save=False)

        if arquivo_video is not None and instance.arquivo_video:
            instance.arquivo_video.delete(save=False)

        return super().update(instance, validated_data)


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
